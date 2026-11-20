"""Download supplied Lex.uz URLs into local JSON, SQLite and RAG chunks.
Run only where access and reuse are permitted. Never bypass site restrictions.
"""
import argparse, datetime, hashlib, json, pathlib, re, sqlite3, time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parent
UA='QonunRadarResearchBot/0.1 (hackathon prototype; contact site operator for permissions)'


def allowed(url, session):
    p = urlparse(url)
    rp = RobotFileParser()
    robots = f"{p.scheme}://{p.netloc}/robots.txt"

    try:
        r = session.get(
            robots,
            timeout=20,
            headers={"User-Agent": UA}
        )

        if r.status_code == 404:
            return True, "robots.txt not found"

        if r.status_code != 200:
            return False, f"robots.txt unavailable (HTTP {r.status_code})"

        rp.parse(r.text.splitlines())
        return rp.can_fetch(UA, url), "robots.txt check"

    except requests.RequestException as exc:
        return False, f"robots.txt unavailable: {exc}"


def extract(html):
    soup=BeautifulSoup(html,'html.parser')
    title=(soup.title.get_text(' ',strip=True) if soup.title else None)
    # Lex.uz markup can change; conservative broad extraction with review required.
    for node in soup(['script','style','nav','footer','header']):node.decompose()
    candidates=[]
    for selector in ['.document-content','.documentText','#documentContent','.doc-content','article','main']:
        candidates += soup.select(selector)
    node=max(candidates,key=lambda n:len(n.get_text(' ',strip=True)),default=soup.body or soup)
    text=node.get_text('\n',strip=True)
    text=re.sub(r'\n{3,}','\n\n',text)
    return title,text

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--delay',type=float,default=20)
    parser.add_argument('--limit',type=int,default=0)
    args=parser.parse_args()
    path=ROOT/'qonunradar_laws.json'; payload=json.loads(path.read_text(encoding='utf-8'))
    session=requests.Session(); session.headers.update({'User-Agent':UA})
    count=0
    for record in payload['laws']:
        if args.limit and count>=args.limit:break
        url=record['source_url']
        ok,reason=allowed(url,session)
        if not ok:
            record['extraction_status']='skipped: '+reason; print(record['law_id'],reason);continue
        try:
            resp=session.get(url,timeout=40)
            resp.raise_for_status()
            title,body=extract(resp.text)
            if len(body)<500: raise ValueError('Extracted text too short; possible JS page or block')
            record['title']=title or record['title']
            record['full_text']=body
            record['retrieved_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
            record['content_sha256']=hashlib.sha256(body.encode()).hexdigest()
            record['extraction_status']='downloaded_unreviewed'
            record['verified']=False
            count+=1;print('Downloaded',record['law_id'],len(body),'chars')
        except (requests.RequestException,ValueError) as exc:
            record['extraction_status']='error: '+str(exc)[:180];print('Failed',record['law_id'],exc)
        finally:
            path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
            time.sleep(max(args.delay,20))
    with sqlite3.connect(ROOT/'qonunradar.db') as con:
        con.execute('CREATE TABLE IF NOT EXISTS laws (law_id TEXT PRIMARY KEY, source_url TEXT, language TEXT, title TEXT, full_text TEXT, retrieved_at TEXT, content_sha256 TEXT, extraction_status TEXT, verified INTEGER)')
        con.execute('CREATE VIRTUAL TABLE IF NOT EXISTS law_chunks USING fts5(law_id UNINDEXED, chunk_text, source_url UNINDEXED)')
        con.execute('DELETE FROM law_chunks')
        chunks=[]
        for rec in payload['laws']:
            con.execute('INSERT OR REPLACE INTO laws VALUES (?,?,?,?,?,?,?,?,?)',(rec['law_id'],rec['source_url'],rec['language'],rec['title'],rec['full_text'],rec['retrieved_at'],rec['content_sha256'],rec['extraction_status'],int(rec['verified'])))
            if not rec['full_text']:continue
            text=rec['full_text']
            for i in range(0,len(text),1200):
                part=text[i:i+1400]
                chunks.append({'law_id':rec['law_id'],'chunk_id':f"{rec['law_id']}-{i//1200}",'text':part,'source_url':rec['source_url'],'verified':False})
                con.execute('INSERT INTO law_chunks VALUES (?,?,?)',(rec['law_id'],part,rec['source_url']))
        (ROOT/'legal_chunks.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in chunks),encoding='utf-8')
    print('Done. Downloaded documents remain UNVERIFIED; review extraction and applicable versions.')
if __name__=='__main__':main()
