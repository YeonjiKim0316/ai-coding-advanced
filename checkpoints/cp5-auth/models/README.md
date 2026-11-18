# models

> © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 · [LICENSE.md](../LICENSE.md)

이 폴더에 AI 모델 파일 두 개가 들어갑니다.

- `model_quantized.onnx`
- `tokenizer.json`

서버는 이 폴더를 먼저 봅니다. 파일이 없으면 Hugging Face 저장소 `thisispaperdoll/review-thermo-onnx`에서 내려받습니다.
모델의 원본은 `daekeun-ml/koelectra-small-v3-nsmc`(MIT)입니다.
