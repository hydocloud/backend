# Login
Login service for hydo platform

## Pre requirements
1. All functions need to perform onboarding phase
2. Exchange key with Hydo steward
3. Connection to EFS
4. User on EFS

## Code Flow
### Generate session parameters
1. Expose GET Api without asking parameters
2. Generate qrcode with [qrcode · PyPI](https://pypi.org/project/qrcode/)
	1. Session id -> aws_request_id from context object
	2. Service uuid  -> hardcoded value
	3. Generate jwt token to authenticate polling
3. Store into dynamodb session_id + status value (PENDING)

### Allow login
1. Create wallet
2. Perform onboarding
3. Receive crypted message from Proof service
4. Store nonce into dynamodb

## Validate user message
1. Receive crypted message from user
2. Get proof's message from dynamodb
3. Decrypt both
4. Compare nonce
5. If true change session_id status to OK

### Generata JWT Token
1. Expose GET Api with session_id parameter
2. Check on dynamodb, session_status
3. If status is ok generate JWT based on AWS Cognito