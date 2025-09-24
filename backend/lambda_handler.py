"""
AWS Lambda handler for FastAPI application
"""
from mangum import Mangum
from main import app

# Create Lambda handler
handler = Mangum(app, lifespan="off")

# Export for AWS Lambda
lambda_handler = handler