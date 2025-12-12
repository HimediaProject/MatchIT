-- Extracted data from Docker DB
-- Generated: 2025-12-11T16:25:50.693612


-- CAREERLEVELS (3 rows)
INSERT INTO careerlevels (careerlevelid, careername, experiencerangeid) VALUES
(1, '학생', NULL),
(2, '신입', NULL),
(3, '경력', NULL);

-- EXPERIENCERANGES (4 rows)
INSERT INTO experienceranges (rangeid, rangename, minyears, maxyears) VALUES
(1, '1년 미만', 0, 1),
(2, '1~3년', 1, 3),
(3, '3~5년', 3, 5),
(4, '5년 이상', 5, NULL);

-- PLATFORMS (3 rows)
INSERT INTO platforms (platformid, platformname) VALUES
(1, 'Saramin'),
(2, 'JobKorea'),
(3, 'Wanted');

-- JOBCATEGORIES (3 rows)
INSERT INTO jobcategories (categoryid, categoryname, parentcategoryid, depth) VALUES
(1, '개발', NULL, 1),
(2, '디자인', NULL, 1),
(3, '마케팅', NULL, 1);

-- SKILLS (6 rows)
INSERT INTO skills (skillid, skillname) VALUES
(1, 'Python'),
(2, 'JavaScript'),
(3, 'SQL'),
(4, 'FastAPI'),
(5, 'pytorch'),
(6, 'NewTestSkill');

-- DESIREDJOBS (7 rows)
INSERT INTO desiredjobs (desiredjobid, jobname) VALUES
(1, '백엔드 개발자'),
(2, '프론트엔드 개발자'),
(3, '데이터 엔지니어'),
(4, 'AI 엔지니어'),
(5, '데이터 분석가'),
(6, '화이트해커'),
(7, '빅데이터 관리자');

-- USERS (4 rows)
INSERT INTO users (userid, name, email, careerlevelid, createdat, updatedat, experiencerangeid) VALUES
(1, '홍길동', 'hong@example.com', 1, '2025-12-10T17:31:47.351563', '2025-12-10T17:31:47.351563', NULL),
(2, '김철수', 'kim@example.com', 2, '2025-12-10T17:31:47.351563', '2025-12-10T17:31:47.351563', NULL),
(3, '박영희', 'park@example.com', 2, '2025-12-10T17:31:47.351563', '2025-12-10T17:31:47.351563', NULL),
(4, '김재영', 'kjy931777@naver.com', 3, '2025-12-10T17:38:48.289305', '2025-12-11T16:14:17.810481', 1);

-- SOCIALLOGINS (4 rows)
INSERT INTO sociallogins (socialloginid, userid, provider, provideruserid, linkedat, unlinkedat) VALUES
(1, 1, 'Kakao', 'kakao_001', '2025-12-10T17:31:47.351563', NULL),
(2, 2, 'Naver', 'naver_002', '2025-12-10T17:31:47.351563', NULL),
(3, 3, 'Google', 'google_003', '2025-12-10T17:31:47.351563', NULL),
(4, 4, 'Kakao', '4633440678', '2025-12-10T08:38:48.298656', NULL);

-- JOBPOSTS (3 rows)
INSERT INTO jobposts (postid, platformid, title, companyname, jobcategoryid, employmenttype, experiencerequirement, minexperienceyears, educationrequirement, location, maintasks, qualifications, preferences, benefits, process, salary, posteddate, closedate, viewcount, url, isactive, createdat, updatedat) VALUES
(2, 2, '프론트엔드 개발자 채용', 'B회사', 1, '계약직', '신입', 0, '학사 이상', '부산', '웹 프론트 개발', 'React 능숙자', '유연 근무', '복지 제공', '서류 -> 코딩 테스트', '3500만원', '2025-11-15', '2025-12-15', 4, NULL, TRUE, '2025-12-10T17:31:47.351563', '2025-12-11T15:43:24.969593'),
(1, 1, '백엔드 개발자 모집', 'A회사', 1, '정규직', '경력', 3, '학사 이상', '서울', '서버 개발 및 운영', 'Java 경험자', '원격근무 가능', '연봉 5000만원', '서류 -> 면접', '5000만원 이상', '2025-11-01', '2025-12-01', 3, NULL, TRUE, '2025-12-10T17:31:47.351563', '2025-12-11T15:47:10.678332'),
(3, 3, '데이터 엔지니어 구함', 'C회사', 1, '정규직', '경력', 2, '학사 이상', '원격', '데이터 파이프라인 구축', 'Python, SQL 숙련자', '주 4일 근무', '스톡옵션', '서류 -> 면접', '6000만원', '2025-11-20', '2025-12-20', 10, NULL, TRUE, '2025-12-10T17:31:47.351563', '2025-12-11T15:57:31.347383');

-- JOBPOSTSKILLS (3 rows)
INSERT INTO jobpostskills (postid, skillid) VALUES
(1, 2),
(2, 2),
(3, 1);

-- BOOTCAMPPOSTS (3 rows)
INSERT INTO bootcampposts (bootcampid, title, institutename, jobcategoryid, location, onlineoffline, costsupporttype, educationcontent, qualification, benefits, startdate, registrationdate, closedate, detailurl, viewcount, createdat, updatedat) VALUES
(2, '리액트 부트캠프', '프론트캠프', 1, '부산', '오프라인', '본인부담', 'React 기초부터 심화', '고등학교 졸업 이상', '취업 연계', '2026-01-05', '2025-12-01', '2025-12-30', 'http://bootcamp2.example.com', 10, '2025-12-10T17:31:47.351563', '2025-12-11T16:01:09.755182'),
(3, '데이터 엔지니어링 부트캠프', '데이터캠퍼스', 1, '원격', '혼합형', '국비지원', '빅데이터 처리, ETL', '학사 이상', '프로젝트 실습', '2026-02-01', '2026-01-01', '2026-01-20', 'http://bootcamp3.example.com', 24, '2025-12-10T17:31:47.351563', '2025-12-11T16:14:15.280615'),
(1, '파이썬 부트캠프', '코드스쿨', 1, '서울', '온라인', '국비지원', 'Python 기본, 데이터 분석', '없음', '수료증 발급', '2025-12-01', '2025-11-01', '2025-11-25', 'http://bootcamp1.example.com', 2, '2025-12-10T17:31:47.351563', '2025-12-11T15:47:35.962901');

-- USERSKILLS (5 rows)
INSERT INTO userskills (userid, skillid) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 3),
(4, 4);

-- USERDESIREDJOBS (5 rows)
INSERT INTO userdesiredjobs (userid, desiredjobid) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 5),
(4, 7);

-- USERSCRAPS (3 rows)
INSERT INTO userscraps (scrapid, userid, posttype, jobpostid, bootcamppostid, scrappedat) VALUES
(1, 1, 'Job', 1, NULL, '2025-12-10T17:31:47.351563'),
(2, 2, 'Job', 2, NULL, '2025-12-10T17:31:47.351563'),
(3, 3, 'Bootcamp', NULL, 3, '2025-12-10T17:31:47.351563');

-- USERNOTIFICATIONSETTINGS (3 rows)
INSERT INTO usernotificationsettings (usernotificationid, userid, notificationtype, isenabled, notificationtime) VALUES
(1, 1, '채용 알림', TRUE, '09:00'),
(2, 2, '맞춤형 정보', FALSE, '12:00'),
(3, 3, '이벤트 소식', TRUE, '18:00');