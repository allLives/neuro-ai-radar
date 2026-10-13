"""Regression tests use synthetic fixtures only; no live API requests or archive writes."""
import contextlib
import datetime as dt
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import shutil
import tempfile
import unittest
import urllib.error
import urllib.parse
from unittest import mock

BASE=pathlib.Path(__file__).resolve().parents[1]

def load(name,file):
    spec=importlib.util.spec_from_file_location(name,BASE/file)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
radar=load('neuro_radar','scripts/update_digest.py')
builder=load('neuro_build','scripts/build.py')
START=dt.date(2026,10,5);END=dt.date(2026,10,11)


def paper(**changes):
    p=dict(id='fixture',title='World Models with JEPA for Continual Robot Planning',
           abstract='Robot world model latent planning.',category='世界模型',date='2026-10-07',venue='arXiv',
           url='https://arxiv.org/abs/2610.00001',kind='preprint',source='arXiv')
    p.update(changes);return p


class DigestTests(unittest.TestCase):
    def test_date_filter(self):
        for date in ('2026-10-05','2026-10-07','2026-10-11'):
            self.assertTrue(radar.date_in_range(date,START,END))
        for date in ('2026-10-04','2026-10-12','unknown',None):
            self.assertFalse(radar.date_in_range(date,START,END))

    def test_paper_dedup_and_quality_filter(self):
        a=paper();b=paper(url=a['url']+'v2')
        late=paper(title='Novel Robot World Models',date='2026-10-13')
        unrelated=paper(title='A Culinary History of Salad',abstract='A short food review.',venue='Nature')
        papers=radar.dedupe_and_rank([a,b,late,unrelated],set(),START,END)
        self.assertEqual(len(papers),1);self.assertEqual(papers[0]['category'],'世界模型')

    def test_doi_dedup_prefers_publication(self):
        a=paper(doi='https://doi.org/10.1234/TEST')
        b=paper(title='World Models for Robot Planning: A Published Version',url='https://doi.org/10.1234/test',
                doi='10.1234/test',kind='journal',venue_indexed=True,abstract='A robot world model.')
        selected=radar.dedupe_and_rank([a,b],set(),START,END)
        self.assertEqual(len(selected),1);self.assertEqual(selected[0]['kind'],'journal')
        self.assertEqual(selected[0]['doi'],'10.1234/test')

    def test_dedup_keeps_fuller_abstract(self):
        selected=radar.dedupe_and_rank([paper(),paper(abstract='World model for robot learning. '*20)],set(),START,END)
        self.assertEqual(len(selected),1);self.assertGreater(len(selected[0]['abstract']),100)

    def test_previous_issue_doi_excluded(self):
        p=paper(doi='10.1234/test')
        selected=radar.dedupe_and_rank([p],{'doi:10.1234/test'},START,END)
        self.assertEqual(selected,[])

    def test_reject_keyword_noise_and_unsafe_links(self):
        records=[paper(title='LLM hallucinations in financial documents',abstract='Language model hallucination tests.'),
                 paper(title='Free energy in molecular cells',abstract='Thermodynamic free energy analysis.',venue='Science'),
                 paper(title='Continual Learning for Financial Earnings Call Speech',abstract='Neural meta-learning methods.'),
                 paper(title='Self-awareness of fall risk in older patients with osteoporosis',abstract='Human self-awareness questionnaire.',kind='journal',venue='Nature'),
                 paper(url='javascript:alert(1)'),paper(url='https://user:password@example.org/paper')]
        self.assertEqual(radar.dedupe_and_rank(records,set(),START,END),[])

    def test_unknown_repository_and_unindexed_journal_excluded(self):
        records=[paper(kind='unknown',venue='Zenodo'),paper(venue='Zenodo'),
                 paper(kind='journal',venue='Unindexed Journal',venue_indexed=False)]
        self.assertEqual(radar.dedupe_and_rank(records,set(),START,END),[])

    def test_source_type_does_not_claim_journal_for_preprint(self):
        self.assertEqual(radar.openalex_kind({'type':'preprint','primary_location':{'source':{'display_name':'Research Square'}}}),'preprint')
        self.assertEqual(radar.openalex_kind({'type':'article','primary_location':{'source':{'type':'repository'}}}),'unknown')
        self.assertEqual(radar.openalex_kind({'type':'article','primary_location':{'is_published':True,'source':{'type':'journal'}}}),'journal')
        self.assertEqual(radar.openalex_kind({'type':'proceedings-article'}),'conference')

    def test_europepmc_core_abstract_and_no_indexing_date_substitution(self):
        payload={'resultList':{'result':[
            {'id':'one','source':'PPR','title':'Consciousness in the human brain','firstPublicationDate':'2026-10-07',
             'doi':'10.1234/test','abstractText':'<h4>Results</h4>Brain &amp; cognition.','pubTypeList':{'pubType':['Preprint']}},
            {'id':'two','source':'MED','title':'No actual publication date','firstIndexDate':'2026-10-07'}]}}
        with mock.patch.object(radar,'get_json',return_value=payload) as fetch:
            records=radar.from_europepmc(START,END)
        self.assertEqual(len(records),1);self.assertEqual(records[0]['kind'],'preprint')
        self.assertEqual(records[0]['abstract'],'Results Brain & cognition.')
        self.assertIn('resultType=core',fetch.call_args.args[0])

    def test_arxiv_date_scoped_and_keeps_doi(self):
        xml='''<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom"><entry>
        <id>http://arxiv.org/abs/2610.00001v2</id><published>2026-10-07T12:00:00Z</published>
        <title>World Models for Robots</title><summary>World models learn robot behavior.</summary>
        <arxiv:doi>10.1234/test</arxiv:doi></entry></feed>'''
        with mock.patch.object(radar,'get_xml',return_value=radar.ET.fromstring(xml)) as fetch, mock.patch.object(radar.time,'sleep'):
            records=radar.from_arxiv(START,END)
        q=urllib.parse.parse_qs(urllib.parse.urlsplit(fetch.call_args.args[0]).query)['search_query'][0]
        self.assertIn('submittedDate:[202610050000 TO 202610112359]',q)
        self.assertEqual(records[0]['doi'],'10.1234/test');self.assertEqual(records[0]['kind'],'preprint')

    def test_fallback_does_not_fake_reading(self):
        issue={'articles':[paper()], 'deepdives':[]}
        with mock.patch.dict(os.environ,{},clear=True):radar.fallback(issue)
        a=issue['articles'][0]
        self.assertIn('尚未生成 AI 解读',a['evidence']);self.assertIn('摘要摘录',a['summary'])
        self.assertIn('abstract',a);self.assertEqual(a['ai_status'],'not_generated')
        self.assertEqual(issue['deepdives'],[])

    def test_ai_missing_abstract_never_generates_analysis(self):
        issue={'articles':[paper(abstract='')], 'deepdives':[]}
        with mock.patch.dict(os.environ,{'OPENAI_API_KEY':'synthetic-test-key'}),mock.patch.object(radar.urllib.request,'urlopen') as call:
            radar.ai_commentary(issue)
        call.assert_not_called();self.assertNotEqual(issue['articles'][0]['ai_status'],'generated')

    def test_ai_partial_response_does_not_edit_bibliography(self):
        issue={'articles':[paper(id='one'),paper(id='two',abstract='')], 'deepdives':[]}
        output=dict(topline='摘要概览',briefs=[dict(id='one',summary='作者报告研究方法。',angle='可检验预测。',
                     title='Malicious replacement',url='https://wrong.example',level='重点精读'),
                     dict(id='two',summary='No evidence')],
                    deepdives=[dict(id='one',headline='假设',insight='可能相关',experiment='比较模型'),
                               dict(id='two',headline='No evidence',insight='Unknown',experiment='Unknown')])
        response=io.BytesIO(json.dumps({'choices':[{'message':{'content':json.dumps(output)}}]}).encode())
        with mock.patch.dict(os.environ,{'OPENAI_API_KEY':'synthetic-test-key','OPENAI_MODEL':'configured-model'}),mock.patch.object(radar.urllib.request,'urlopen',return_value=response) as call:
            result=radar.ai_commentary(issue)
        self.assertEqual(result['articles'][0]['title'],paper()['title'])
        self.assertEqual(result['articles'][0]['url'],paper()['url'])
        self.assertEqual(result['articles'][1]['ai_status'],'unavailable')
        self.assertEqual(len(result['deepdives']),1);self.assertIn('模型推测',result['deepdives'][0]['insight'])
        body=json.loads(call.call_args.args[0].data);self.assertEqual(body['model'],'configured-model')
        self.assertEqual(len(json.loads(body['messages'][1]['content'])['论文']),1)

    def test_ai_failure_still_archivable(self):
        issue={'articles':[paper()], 'deepdives':[]}
        with mock.patch.dict(os.environ,{'OPENAI_API_KEY':'synthetic-test-key'}),mock.patch.object(radar.urllib.request,'urlopen',side_effect=TimeoutError('timeout')):
            result=radar.ai_commentary(issue)
        self.assertEqual(result['articles'][0]['ai_status'],'unavailable')
        self.assertEqual(result['deepdives'],[])

    def test_openalex_budget_failure_stops_source(self):
        error=urllib.error.HTTPError('https://api.openalex.org/works',429,'quota exhausted',{},None)
        with mock.patch.object(radar.urllib.request,'urlopen',side_effect=error) as fetch:
            records=radar.from_openalex(START,END)
        self.assertEqual(records,[]);self.assertEqual(fetch.call_count,1)
        self.assertEqual(radar.SOURCE_STATUS['OpenAlex']['failed_requests'],1)

    def test_credentials_redacted_from_errors(self):
        with mock.patch.dict(os.environ,{'OPENALEX_API_KEY':'synthetic-secret'}):
            text=radar.safe_error(Exception('https://example.org?api_key=synthetic-secret&x=1'))
        self.assertNotIn('synthetic-secret',text)

    def test_existing_edition_preserved_exactly(self):
        manifest=json.loads((BASE/'data/index.json').read_text())
        self.assertIn('2026-W41',[w['id'] for w in manifest['weeks']])
        data=(BASE/'data/weeks/2026-W41.json').read_bytes();issue=json.loads(data)
        self.assertEqual(hashlib.sha256(data).hexdigest(),'bb469dd4516fb099e56bd9dbbea6eb5722873504bcd94b2ba7ad07b10bc9700b')
        self.assertEqual(len(issue['articles']),25);self.assertEqual(len(issue['deepdives']),5)
        builder.validate_issue(issue,'2026-W41')

    def test_existing_week_skips_all_network(self):
        with mock.patch('sys.argv',['update','--date','2026-10-13']),mock.patch.object(radar,'from_openalex') as fetch:
            radar.main()
        fetch.assert_not_called()

    def test_iso_year_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);(root/'data/weeks').mkdir(parents=True)
            (root/'data/weeks/2020-W53.json').write_text('{}')
            with mock.patch.object(radar,'ROOT',root),mock.patch('sys.argv',['update','--date','2021-01-04']),mock.patch.object(radar,'from_openalex') as fetch:
                radar.main()
            fetch.assert_not_called()

    def test_api_failure_leaves_all_archives_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);shutil.copytree(BASE/'data',root/'data')
            before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*.json')}
            with mock.patch.object(radar,'ROOT',root),mock.patch('sys.argv',['update','--date','2026-10-05']),mock.patch.object(radar,'from_openalex',return_value=[]),mock.patch.object(radar,'from_arxiv',return_value=[]),mock.patch.object(radar,'from_europepmc',return_value=[]):
                with self.assertRaises(SystemExit) as err:radar.main()
            self.assertEqual(err.exception.code,2)
            self.assertEqual(before,{str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*.json')})

    def test_archive_write_never_overwrites_and_rolls_back_index_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);week=root/'weeks/test.json';index=root/'index.json';index.write_text('original')
            radar.save_archive(week,index,{'title':'first'},{'weeks':['first']})
            with self.assertRaises(FileExistsError):radar.save_archive(week,index,{'title':'second'},{})
            self.assertEqual(json.loads(week.read_text())['title'],'first')
            new=root/'weeks/new.json';before=index.read_bytes()
            with mock.patch.object(radar.os,'replace',side_effect=OSError('Disk error')):
                with self.assertRaises(OSError):radar.save_archive(new,index,{}, {})
            self.assertFalse(new.exists());self.assertEqual(index.read_bytes(),before)
            self.assertEqual(sorted(p.name for p in (root/'weeks').iterdir()),['test.json'])

    def test_one_source_outage_allows_archive_and_check_never_writes(self):
        for mode in ('update','check'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as tmp:
                root=pathlib.Path(tmp);shutil.copytree(BASE/'data',root/'data')
                records=[paper(title=f'World Models for Robot Learning Fixture {i}',url=f'https://arxiv.org/abs/2609.0000{i}',date='2026-10-01') for i in range(5)]
                argv=['update','--date','2026-10-05']+(['--check'] if mode=='check' else [])
                with mock.patch.object(radar,'ROOT',root),mock.patch('sys.argv',argv),mock.patch.dict(os.environ,{},clear=True),mock.patch.object(radar,'from_openalex',return_value=[]),mock.patch.object(radar,'from_arxiv',return_value=records),mock.patch.object(radar,'from_europepmc',return_value=[]),contextlib.redirect_stdout(io.StringIO()):
                    radar.main()
                path=root/'data/weeks/2026-W40.json'
                self.assertEqual(path.exists(),mode=='update')
                if path.exists():
                    issue=json.loads(path.read_text());self.assertEqual(len(issue['articles']),5)
                    self.assertTrue(all(a['ai_status']=='not_generated' for a in issue['articles']))
                    self.assertIn('2026-W40',[w['id'] for w in json.loads((root/'data/index.json').read_text())['weeks']])

    def test_build_removes_stale_and_private_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);shutil.copytree(BASE/'data',root/'data');shutil.copytree(BASE/'assets',root/'assets')
            shutil.copy2(BASE/'index.html',root/'index.html');(root/'dist').mkdir()
            (root/'dist/old-secret.txt').write_text('synthetic');(root/'assets/.env').write_text('synthetic')
            builder.build(root)
            self.assertFalse((root/'dist/old-secret.txt').exists());self.assertFalse((root/'dist/assets/.env').exists())
            self.assertEqual({p.name for p in (root/'dist/assets').iterdir()},set(builder.PUBLIC_ASSETS))
            self.assertTrue((root/'dist/.nojekyll').exists())

    def test_build_fails_for_missing_manifest_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);shutil.copytree(BASE/'data',root/'data')
            index=json.loads((root/'data/index.json').read_text());index['weeks'].append({'id':'2026-W39'})
            (root/'data/index.json').write_text(json.dumps(index))
            with self.assertRaisesRegex(ValueError,'missing archives'):builder.build(root)

if __name__=='__main__':unittest.main()
