# AWS Checklist For Step 2

Use this checklist to finish the AWS-specific infrastructure for step 2.

## 1. Verify DVC remote

Your repo already points DVC to S3:

```bash
cat .dvc/config
```

Expected remote:

```ini
[core]
    remote = myremote
['remote "myremote"']
    url = s3://day21-hoanglm-vinai/dvc
```

If your local AWS CLI is configured, push the tracked datasets:

```bash
dvc push
```

## 2. Create or prepare the EC2 instance

Recommended baseline:

- OS: Ubuntu 22.04
- Inbound rules: `22/tcp` for SSH, `8000/tcp` for FastAPI
- IAM role: allow `s3:GetObject` on `arn:aws:s3:::day21-hoanglm-vinai/models/latest/model.pkl`

Example packages on the VM:

```bash
sudo apt update
sudo apt install -y python3-pip
pip3 install -r requirements.txt
mkdir -p ~/models ~/src
```

If you do not clone the repo on the VM, the minimum packages are:

```bash
pip3 install fastapi uvicorn scikit-learn joblib boto3
mkdir -p ~/models ~/src
```

## 3. Copy the serving code to EC2

Copy [`src/serve.py`](/c:/Users/My Asus/Desktop/AI_thucchien/Day21-Track2-CI-CD-for-AI-Systems/src/serve.py) to `~/src/serve.py` on the instance.

## 4. Create the systemd service

Use [`deploy/mlops-serve.service.example`](/c:/Users/My Asus/Desktop/AI_thucchien/Day21-Track2-CI-CD-for-AI-Systems/deploy/mlops-serve.service.example) as the template.

On the VM:

```bash
sudo cp deploy/mlops-serve.service.example /etc/systemd/system/mlops-serve.service
sudo systemctl daemon-reload
sudo systemctl enable mlops-serve
```

If your VM username is not `ubuntu`, update `User`, `WorkingDirectory`, and `ExecStart` first.

## 5. Create the GitHub deploy SSH key

On your local machine:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/mlops_deploy -N "" -C "github-actions-deploy"
```

Append the public key to the VM:

```bash
cat ~/.ssh/mlops_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## 6. Add GitHub Actions secrets

Required secrets:

- `CLOUD_CREDENTIALS`
- `CLOUD_BUCKET`
- `VM_HOST`
- `VM_USER`
- `VM_SSH_KEY`

For AWS, set `CLOUD_CREDENTIALS` to:

```json
{"aws_access_key_id":"YOUR_KEY","aws_secret_access_key":"YOUR_SECRET","aws_default_region":"us-east-2"}
```

`VM_SSH_KEY` must be the full private key content from `~/.ssh/mlops_deploy`.

## 7. Run the first pipeline

Push your branch:

```bash
git add .
git commit -m "feat: complete step 2 aws pipeline"
git push origin main
```

Then check GitHub Actions for the four jobs:

- `Test`
- `Train`
- `Eval`
- `Deploy`

## 8. Smoke test the API

After the first successful deploy:

```bash
curl http://<VM_IP>:8000/health
```

Expected:

```json
{"status":"ok"}
```

Prediction test:

```bash
curl -X POST http://<VM_IP>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[7.4,0.70,0.00,1.9,0.076,11.0,34.0,0.9978,3.51,0.56,9.4,0]}'
```

Expected shape:

```json
{"prediction":0,"label":"thap"}
```

## 9. Troubleshooting

If deploy fails, inspect:

```bash
sudo journalctl -u mlops-serve -n 50
systemctl status mlops-serve
```

Common causes:

- `CLOUD_BUCKET` is wrong in the service file
- the EC2 security group does not allow port `8000`
- the EC2 instance has no S3 read permission
- `models/latest/model.pkl` has not been uploaded yet
