-- 판매자 로그인용 비밀번호 해시 (비밀번호 원문은 저장하지 않는다)
ALTER TABLE sellers ADD COLUMN password_hash TEXT;

-- © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
