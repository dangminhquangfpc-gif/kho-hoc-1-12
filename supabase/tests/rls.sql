BEGIN;
INSERT INTO auth.users VALUES('00000000-0000-0000-0000-000000000001'),('00000000-0000-0000-0000-000000000002');
INSERT INTO public.subjects VALUES('toan','Toán') ON CONFLICT DO NOTHING;
INSERT INTO public.content_sources(id,title,source_type,license,rights_evidence,redistribution_allowed,verified_at) VALUES('10000000-0000-0000-0000-000000000001','Fixture','original','original_content','Test',true,now());
INSERT INTO public.questions(id,grade_id,subject_id,topic,type,content,normalized_content,source_id,publication_status) VALUES('20000000-0000-0000-0000-000000000001',5,'toan','test','numeric','Public?','public','10000000-0000-0000-0000-000000000001','published'),('20000000-0000-0000-0000-000000000002',5,'toan','test','numeric','Draft?','draft','10000000-0000-0000-0000-000000000001','draft');
INSERT INTO public.question_versions(question_id,version,answer_payload,max_score) VALUES('20000000-0000-0000-0000-000000000001',1,'{"correct_answer":["secret"]}',1);
INSERT INTO public.exam_attempts(id,user_id,status) VALUES('30000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','graded'),('30000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000002','graded');
INSERT INTO public.grading_results(attempt_id,grading_method,raw_score,max_score,grading_status) VALUES('30000000-0000-0000-0000-000000000001','answer_key',1,1,'graded'),('30000000-0000-0000-0000-000000000002','answer_key',1,1,'graded');
SET LOCAL ROLE anon;
DO $$ BEGIN
 IF (SELECT count(*) FROM public.questions) <> 1 THEN RAISE EXCEPTION 'Draft leaked or published missing'; END IF;
 BEGIN PERFORM * FROM public.question_versions; RAISE EXCEPTION 'Answers leaked'; EXCEPTION WHEN insufficient_privilege THEN NULL; END;
 BEGIN INSERT INTO public.user_roles VALUES('00000000-0000-0000-0000-000000000002','admin'); RAISE EXCEPTION 'Role escalation'; EXCEPTION WHEN insufficient_privilege THEN NULL; END;
END $$;
RESET ROLE;
SET LOCAL ROLE authenticated;
SET LOCAL request.jwt.claim.sub = '00000000-0000-0000-0000-000000000001';
DO $$ BEGIN
 IF (SELECT count(*) FROM public.exam_attempts) <> 1 THEN RAISE EXCEPTION 'Other student attempt leaked'; END IF;
 IF (SELECT count(*) FROM public.grading_results) <> 1 THEN RAISE EXCEPTION 'Other student results leaked'; END IF;
 BEGIN UPDATE public.grading_results SET raw_score = 0; RAISE EXCEPTION 'Score tampering'; EXCEPTION WHEN insufficient_privilege THEN NULL; END;
 BEGIN PERFORM guest_token_hash FROM public.exam_attempts; RAISE EXCEPTION 'Guest hash leaked'; EXCEPTION WHEN insufficient_privilege THEN NULL; END;
END $$;
RESET ROLE;
ROLLBACK;
