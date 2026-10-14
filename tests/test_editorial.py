"""Editorial supplements must preserve sources and fail safely."""
import copy
import hashlib
import json
import pathlib
import shutil
import tempfile
import unittest
from scripts.editorial import apply_editorial, topic_title
from scripts.build import build


class EditorialTests(unittest.TestCase):
    def setUp(self):
        self.issue={'id':'2026-W40','title':'本周神经科学 × AI 精选','articles':[{'id':'one','title':'Original title','url':'https://example.org/paper','doi':'10.1/source','date':'2026-10-01','category':'世界模型','abstract':'An observed result.'}], 'deepdives':[]}
        self.raw=json.dumps(self.issue).encode()
        self.supplement={'version':1,'id':'2026-W40','source_sha256':hashlib.sha256(self.raw).hexdigest(),'editor':'Fixture','basis':'abstracts','edited_at':'2026-10-14','title':'世界模型如何表达行动','subtitle':'Fixture subtitle','topline':'Fixture introduction','briefs':[{'id':'one','title_zh':'中文标题','summary':'作者报告一个结果。'}],'highlights':[{'id':'one','headline':'先读这篇','summary':'一个研究问题。'}]}

    def test_supplement_preserves_source_and_bibliography(self):
        before=copy.deepcopy(self.issue)
        result=apply_editorial(self.issue,self.supplement,self.raw)
        self.assertEqual(self.issue,before)
        for key in ('title','url','doi','date','abstract'):
            self.assertEqual(result['articles'][0][key],before['articles'][0][key])
        self.assertEqual(result['articles'][0]['title_zh'],'中文标题')

    def test_rejects_stale_source_and_bibliography_edits(self):
        for change in ('hash','url','unknown','duplicate'):
            s=copy.deepcopy(self.supplement)
            if change=='hash':s['source_sha256']='0'*64
            if change=='url':s['briefs'][0]['url']='https://wrong.example'
            if change=='unknown':s['highlights'][0]['id']='missing'
            if change=='duplicate':s['briefs']*=2
            with self.subTest(change=change),self.assertRaises(ValueError):apply_editorial(self.issue,s,self.raw)

    def test_missing_abstract_cannot_gain_new_analysis(self):
        self.issue['articles'][0]['abstract']=''
        raw=json.dumps(self.issue).encode();self.supplement['source_sha256']=hashlib.sha256(raw).hexdigest()
        with self.assertRaises(ValueError):apply_editorial(self.issue,self.supplement,raw)

    def test_pending_issue_gets_topic_title_without_fake_summary(self):
        result=apply_editorial(self.issue,None,self.raw)
        self.assertEqual(result['title'],'世界模型')
        self.assertNotIn('summary',result['articles'][0])
        self.assertNotIn('editorial',result)
        self.assertEqual(topic_title([{'category':'梦与幻觉'}]),'梦与想象')

    def test_build_publishes_supplement_without_rewriting_archive(self):
        base=pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);(root/'data/weeks').mkdir(parents=True);(root/'data/editorial').mkdir()
            self.issue.update(from_date='2026-09-28',to_date='2026-10-04')
            raw=json.dumps(self.issue).encode();self.supplement['source_sha256']=hashlib.sha256(raw).hexdigest()
            source=root/'data/weeks/2026-W40.json';source.write_bytes(raw)
            (root/'data/index.json').write_text(json.dumps({'weeks':[{'id':'2026-W40'}]}))
            editorial=root/'data/editorial/2026-W40.json';editorial.write_text(json.dumps(self.supplement))
            shutil.copytree(base/'assets',root/'assets');shutil.copy2(base/'index.html',root/'index.html')
            build(root)
            published=root/'dist/data/weeks/2026-W40.json';before=published.read_bytes()
            self.assertEqual(json.loads(before)['title'],self.supplement['title'])
            self.assertEqual(source.read_bytes(),raw)
            self.supplement['source_sha256']='0'*64;editorial.write_text(json.dumps(self.supplement))
            with self.assertRaises(ValueError):build(root)
            self.assertEqual(published.read_bytes(),before)


if __name__=='__main__':unittest.main()
