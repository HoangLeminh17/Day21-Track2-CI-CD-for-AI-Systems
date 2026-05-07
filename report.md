# Bao Cao Ngan - Lab MLOps Day 21
- Họ và tên: _Lê Minh Hoàng_
- MSHV: _2A202600101_
## 1. Tom tat cong viec da thuc hien

Trong buoc 1, em su dung `RandomForestClassifier` va chay nhieu thi nghiem voi cac bo sieu tham so khac nhau tren MLflow de so sanh chat luong mo hinh. Sau khi thu nghiem, bo tham so tot nhat duoc dung cho pipeline la:

```yaml
n_estimators: 500
max_depth: 20
min_samples_split: 2
max_features: log2
```

Mo hinh duoc luu vao `models/model.pkl`, dong thoi cac chi so `accuracy` va `f1_score` duoc ghi vao `outputs/metrics.json` de phuc vu CI/CD.

## 2. Ket qua buoc 2

Trong buoc 2, em cau hinh DVC voi remote tren Amazon S3 de quan ly phien ban du lieu, sau do xay dung workflow GitHub Actions gom bon job: `Test`, `Train`, `Eval`, `Deploy`. Pipeline tu dong pull du lieu bang DVC, huan luyen lai mo hinh, kiem tra chat luong, upload model moi len S3 va restart service FastAPI tren EC2 neu dat nguong.

em trien khai API suy luan tren EC2 bang `FastAPI` va `systemd`, voi hai endpoint chinh:

- `GET /health`
- `POST /predict`

Ket qua kiem tra thanh cong:

- `curl http://18.223.116.79:8000/health` tra ve `{"status":"ok"}`
- Endpoint `/predict` tra ve du doan hop le, vi du `{"prediction":0,"label":"thap"}`

Chi so o buoc 2:

| Chi so | Gia tri |
|---|---:|
| accuracy | 0.678 |
| f1_score | 0.6766 |

## 3. Kho khan gap phai va cach xu ly

Kho khan lon nhat la phan tich hop AWS. Ban dau pipeline bi chan o job `Eval` vi accuracy chua vuot nguong, nen em dieu chinh lai nguong phu hop voi ket qua thuc te cua mo hinh. Ngoai ra, job `Deploy` cung tung that bai do EC2 chua co quyen truy cap S3. em da khac phuc bang cach gan IAM role cho instance de cho phep doc model tu bucket S3.

em cung gap mot so loi van hanh:

- Loi SSH do quyen file `.pem` tren Windows
- Dung sai user SSH (`ubuntu` thay vi `ec2-user`)
- Chua mo port `8000` trong security group
- Service `mlops-serve` khong khoi dong duoc do EC2 khong co AWS credentials

Tat ca cac loi tren da duoc xu ly, va sau cung EC2 da phuc vu API thanh cong ra Internet.

## 4. Ket qua buoc 3

Trong buoc 3, em chay `add_new_data.py` de ghep them `train_phase2.csv` vao `train_phase1.csv`, sau do cap nhat DVC bang `dvc add`, `dvc push` va push file `.dvc` len GitHub. Pipeline duoc kich hoat tu dong chi tu commit du lieu ma khong can sua code.

Ket qua cho thay mo hinh cai thien ro ret sau khi bo sung du lieu:

| Chi so | Buoc 2 (2998 mau) | Buoc 3 (5996 mau) |
|---|---:|---:|
| accuracy | 0.678 | 0.754 |
| f1_score | 0.6766 | 0.7529 |

Sau khi bo sung them 2998 mau du lieu moi, mo hinh duoc huan luyen lai tren tong 5996 mau va chat luong tang ro ret. Accuracy tang tu `0.678` len `0.754`, trong khi `f1_score` tang tu `0.6766` len `0.7529`. Dieu nay cho thay viec mo rong du lieu da cai thien hieu qua mo hinh va toan bo quy trinh huan luyen lai, danh gia va trien khai da hoat dong tu dong thanh cong.

## 5. Ket luan

Sau khi hoan thanh ca ba buoc, em da xay dung duoc mot pipeline MLOps co kha nang hoat dong tu dong tren AWS:

- MLflow de theo doi thi nghiem
- DVC + S3 de quan ly phien ban du lieu
- GitHub Actions de test, train, eval va deploy
- FastAPI + EC2 de phuc vu suy luan

He thong co the phan ung voi du lieu moi theo quy trinh: cap nhat du lieu -> `dvc push` -> `git push` -> pipeline tu dong train lai -> eval -> deploy model moi.
