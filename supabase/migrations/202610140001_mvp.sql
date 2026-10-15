BEGIN;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE TABLE IF NOT EXISTS public.education_programs (id text PRIMARY KEY, name text NOT NULL, version text NOT NULL);
CREATE TABLE IF NOT EXISTS public.grades (id smallint PRIMARY KEY CHECK(id BETWEEN 1 AND 12), name text NOT NULL);
CREATE TABLE IF NOT EXISTS public.subjects (id text PRIMARY KEY, name text NOT NULL);
CREATE TABLE IF NOT EXISTS public.grade_subjects (program_id text REFERENCES public.education_programs, grade_id smallint REFERENCES public.grades, subject_id text REFERENCES public.subjects, requirement text NOT NULL CHECK(requirement IN ('required','elective','optional')), PRIMARY KEY(program_id,grade_id,subject_id));
CREATE TABLE IF NOT EXISTS public.textbook_series (id text PRIMARY KEY, name text NOT NULL);
CREATE TABLE IF NOT EXISTS public.user_roles (user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE, role text NOT NULL CHECK(role IN ('student','teacher','parent','admin')), PRIMARY KEY(user_id,role));
CREATE TABLE IF NOT EXISTS public.user_profiles (user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE, display_name text, grade_id smallint REFERENCES public.grades);
CREATE TABLE IF NOT EXISTS public.parent_child_links (parent_id uuid REFERENCES auth.users(id) ON DELETE CASCADE, child_id uuid REFERENCES auth.users(id) ON DELETE CASCADE, confirmed_at timestamptz, PRIMARY KEY(parent_id,child_id), CHECK(parent_id <> child_id));
CREATE TABLE IF NOT EXISTS public.content_sources (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), title text NOT NULL, source_type text NOT NULL CHECK(source_type IN ('original','licensed','link_only')), url text, license text NOT NULL, rights_evidence text NOT NULL, redistribution_allowed boolean NOT NULL DEFAULT false, verified_by uuid REFERENCES auth.users(id), verified_at timestamptz);
CREATE TABLE IF NOT EXISTS public.questions (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), external_id text UNIQUE, grade_id smallint NOT NULL REFERENCES public.grades, subject_id text NOT NULL REFERENCES public.subjects, topic text NOT NULL, type text NOT NULL CHECK(type IN ('single_choice','multiple_choice','true_false','short_answer','numeric','essay')), content text NOT NULL, normalized_content text NOT NULL, source_id uuid NOT NULL REFERENCES public.content_sources, publication_status text NOT NULL DEFAULT 'draft' CHECK(publication_status IN ('draft','needs_review','approved','published','rejected','archived','takedown')), created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS public.question_options (question_id uuid REFERENCES public.questions ON DELETE CASCADE, option_id text, content text NOT NULL, PRIMARY KEY(question_id,option_id));
-- Entire version payload is private: answers and rubrics never share a public table.
CREATE TABLE IF NOT EXISTS public.question_versions (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), question_id uuid NOT NULL REFERENCES public.questions ON DELETE CASCADE, version int NOT NULL CHECK(version > 0), answer_payload jsonb NOT NULL, max_score numeric NOT NULL CHECK(max_score > 0), approved_by uuid REFERENCES auth.users(id), approved_at timestamptz, UNIQUE(question_id,version));
CREATE TABLE IF NOT EXISTS public.exams (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), title text NOT NULL, grade_id smallint NOT NULL REFERENCES public.grades, subject_id text NOT NULL REFERENCES public.subjects, program_id text NOT NULL REFERENCES public.education_programs, school_year text, exam_type text NOT NULL DEFAULT 'practice', duration_minutes int NOT NULL CHECK(duration_minutes BETWEEN 1 AND 180), publication_status text NOT NULL DEFAULT 'draft' CHECK(publication_status IN ('draft','approved','published','archived','takedown')));
CREATE TABLE IF NOT EXISTS public.exam_questions (exam_id uuid REFERENCES public.exams ON DELETE CASCADE, question_version_id uuid REFERENCES public.question_versions, position int NOT NULL CHECK(position >= 0), PRIMARY KEY(exam_id,question_version_id), UNIQUE(exam_id,position));
CREATE TABLE IF NOT EXISTS public.exam_attempts (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), exam_id uuid REFERENCES public.exams, user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE, guest_token_hash text, status text NOT NULL DEFAULT 'in_progress' CHECK(status IN ('in_progress','submitted','needs_manual_review','graded')), created_at timestamptz NOT NULL DEFAULT now(), submitted_at timestamptz, CHECK(user_id IS NOT NULL OR guest_token_hash IS NOT NULL));
-- Snapshot contains answer keys; never grant SELECT to client roles.
CREATE TABLE IF NOT EXISTS public.attempt_snapshots (attempt_id uuid PRIMARY KEY REFERENCES public.exam_attempts ON DELETE CASCADE, payload jsonb NOT NULL);
CREATE TABLE IF NOT EXISTS public.student_answers (attempt_id uuid REFERENCES public.exam_attempts ON DELETE CASCADE, question_version_id uuid REFERENCES public.question_versions, answer jsonb NOT NULL, PRIMARY KEY(attempt_id,question_version_id));
CREATE TABLE IF NOT EXISTS public.grading_results (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), attempt_id uuid NOT NULL UNIQUE REFERENCES public.exam_attempts ON DELETE CASCADE, grading_method text NOT NULL, raw_score numeric CHECK(raw_score >= 0), max_score numeric NOT NULL CHECK(max_score > 0), feedback jsonb NOT NULL DEFAULT '{}', confidence numeric CHECK(confidence BETWEEN 0 AND 1), grading_status text NOT NULL CHECK(grading_status IN ('graded','provisional','needs_manual_review')), rubric_version text, model_version text, created_at timestamptz NOT NULL DEFAULT now(), CHECK(raw_score <= max_score));
CREATE TABLE IF NOT EXISTS public.content_reviews (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), question_id uuid REFERENCES public.questions ON DELETE CASCADE, reviewer_id uuid NOT NULL REFERENCES auth.users(id), decision text NOT NULL CHECK(decision IN ('approved','rejected','needs_review')), comment text NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS public.audit_logs (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, actor_id uuid REFERENCES auth.users(id), action text NOT NULL, target text NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS questions_filter ON public.questions(grade_id,subject_id,publication_status);
CREATE INDEX IF NOT EXISTS questions_search ON public.questions USING gin(to_tsvector('simple',normalized_content));
CREATE INDEX IF NOT EXISTS questions_fuzzy ON public.questions USING gin(normalized_content gin_trgm_ops);
CREATE INDEX IF NOT EXISTS attempts_owner ON public.exam_attempts(user_id,created_at);
CREATE INDEX IF NOT EXISTS answers_attempt ON public.student_answers(attempt_id);

CREATE OR REPLACE FUNCTION public.is_admin() RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$ SELECT EXISTS(SELECT 1 FROM public.user_roles WHERE user_id = auth.uid() AND role = 'admin') $$;
REVOKE ALL ON FUNCTION public.is_admin() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.is_admin() TO anon, authenticated;

DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['education_programs','grades','subjects','grade_subjects','textbook_series','user_roles','user_profiles','parent_child_links','content_sources','questions','question_options','question_versions','exams','exam_questions','exam_attempts','attempt_snapshots','student_answers','grading_results','content_reviews','audit_logs'] LOOP
  EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY',t);
  EXECUTE format('REVOKE ALL ON public.%I FROM anon, authenticated',t);
 END LOOP;
END $$;

DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['education_programs','grades','subjects','grade_subjects','textbook_series'] LOOP
  EXECUTE format('DROP POLICY IF EXISTS catalog_read ON public.%I',t);
  EXECUTE format('CREATE POLICY catalog_read ON public.%I FOR SELECT TO anon,authenticated USING (true)',t);
  EXECUTE format('GRANT SELECT ON public.%I TO anon,authenticated',t);
 END LOOP;
END $$;
DROP POLICY IF EXISTS public_questions ON public.questions;
CREATE POLICY public_questions ON public.questions FOR SELECT TO anon,authenticated USING(publication_status = 'published' AND EXISTS(SELECT 1 FROM public.content_sources s WHERE s.id = source_id AND s.redistribution_allowed AND s.verified_at IS NOT NULL));
DROP POLICY IF EXISTS verified_sources ON public.content_sources;
CREATE POLICY verified_sources ON public.content_sources FOR SELECT TO anon,authenticated USING(redistribution_allowed AND verified_at IS NOT NULL);
-- Hide license evidence/reviewer identities from public clients.
GRANT SELECT(id,title,source_type,url,license,redistribution_allowed,verified_at) ON public.content_sources TO anon,authenticated;
GRANT SELECT ON public.questions TO anon,authenticated;
DROP POLICY IF EXISTS public_options ON public.question_options;
CREATE POLICY public_options ON public.question_options FOR SELECT TO anon,authenticated USING(EXISTS(SELECT 1 FROM public.questions q WHERE q.id = question_id));
GRANT SELECT ON public.question_options TO anon,authenticated;
DROP POLICY IF EXISTS public_exams ON public.exams;
CREATE POLICY public_exams ON public.exams FOR SELECT TO anon,authenticated USING(publication_status = 'published');
GRANT SELECT ON public.exams TO anon,authenticated;
DROP POLICY IF EXISTS own_roles ON public.user_roles;
CREATE POLICY own_roles ON public.user_roles FOR SELECT TO authenticated USING(user_id = auth.uid());
GRANT SELECT ON public.user_roles TO authenticated;
DROP POLICY IF EXISTS own_profile ON public.user_profiles;
CREATE POLICY own_profile ON public.user_profiles FOR SELECT TO authenticated USING(user_id = auth.uid());
GRANT SELECT ON public.user_profiles TO authenticated;
DROP POLICY IF EXISTS own_attempts ON public.exam_attempts;
CREATE POLICY own_attempts ON public.exam_attempts FOR SELECT TO authenticated USING(user_id = auth.uid());
-- Guest token hash is server-only.
GRANT SELECT(id,exam_id,user_id,status,created_at,submitted_at) ON public.exam_attempts TO authenticated;
DROP POLICY IF EXISTS own_results ON public.grading_results;
CREATE POLICY own_results ON public.grading_results FOR SELECT TO authenticated USING(EXISTS(SELECT 1 FROM public.exam_attempts a WHERE a.id = attempt_id AND a.user_id = auth.uid() AND a.status <> 'in_progress'));
GRANT SELECT ON public.grading_results TO authenticated;
-- All mutations (including student answers), private versions, snapshots and reviews go through backend authorization.
INSERT INTO public.education_programs VALUES('gdpt-2018','Chương trình GDPT 2018','2018') ON CONFLICT DO NOTHING;
INSERT INTO public.grades SELECT n, 'Lớp '||n FROM generate_series(1,12) n ON CONFLICT DO NOTHING;
COMMIT;
