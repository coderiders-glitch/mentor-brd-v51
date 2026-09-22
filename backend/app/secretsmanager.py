import os
import json
import logging
import urllib.parse

logger = logging.getLogger(__name__)

def _sanitize_db_url(url: str) -> str:
    """Auto-encode special characters like @ in password if present unencoded."""
    if not url or not isinstance(url, str):
        return url
    if url.startswith("postgresql://") or url.startswith("postgres://") or url.startswith("mysql://"):
        prefix, rest = url.split("://", 1)
        if rest.count("@") > 1:
            user_pass, host_db = rest.rsplit("@", 1)
            if ":" in user_pass:
                user, password = user_pass.split(":", 1)
                return f"{prefix}://{user}:{urllib.parse.quote_plus(password)}@{host_db}"
    return url

def get_secret(key: str = None, default: str = None):
    """
    Fetch runtime credentials dynamically from AWS Secrets Manager secret "app_secrets" (region: ap-south-1).
    Usage:
      get_secret("DATABASE_URL") -> Returns string value for DATABASE_URL from AWS Secrets Manager app_secrets
      get_secret() -> Returns full dictionary of secrets from AWS Secrets Manager app_secrets
    """
    target_secret = os.environ.get("AWS_SECRET_NAME") or "app_secrets"
    target_region = os.environ.get("AWS_REGION") or "ap-south-1"

    secrets = {}

    # 1. Fetch from AWS Secrets Manager (Primary source of truth: app_secrets)
    try:
        import boto3
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=target_region,
        )
        response = client.get_secret_value(SecretId=target_secret)
        if 'SecretString' in response:
            remote = json.loads(response['SecretString'])
            if isinstance(remote, dict):
                secrets.update(remote)
                logger.info('Successfully fetched secrets from AWS Secrets Manager: %s', target_secret)
    except Exception as exc:
        logger.warning('Could not fetch secrets from AWS Secrets Manager (%s): %s. Falling back to environment variables.', target_secret, exc)

    # 2. Merge environment variables as secondary fallback
    for k, v in os.environ.items():
        if k not in secrets:
            secrets[k] = v

    if key is not None:
        # A present-but-empty environment value is not a usable secret and must
        # not suppress the caller's explicit default. This preserves the public
        # ``get_secret(key, default)`` contract used by generated integrations.
        val = secrets.get(key)
        if val is None or val == "":
            val = default
        if key in ("DATABASE_URL", "DB_URL") and val:
            return _sanitize_db_url(val)
        if val is not None:
            return val
        return ''

    if "DATABASE_URL" in secrets:
        secrets["DATABASE_URL"] = _sanitize_db_url(secrets["DATABASE_URL"])
    if "DB_URL" in secrets:
        secrets["DB_URL"] = _sanitize_db_url(secrets["DB_URL"])

    return secrets

def get_bedrock_model_id() -> str:
    """Return the Bedrock model configured in the shared app_secrets secret."""
    return get_secret("BEDROCK_MODEL_ID", "zai.glm-5")

def get_aws_region() -> str:
    """Return the AWS region configured for the generated application."""
    return get_secret("AWS_REGION", "ap-south-1")

def get_database_url() -> str:
    """Build the PostgreSQL URL from the canonical app_secrets DB_* keys.

    Falls back to DATABASE_URL in the same secret when component keys are
    missing, so generated apps always share the predefined Postgres instance.
    """
    host = get_secret("DB_HOST")
    port = get_secret("DB_PORT", "5432")
    database = get_secret("DB_NAME")
    user = get_secret("DB_USER")
    password = get_secret("DB_PASSWORD")
    if all((host, database, user, password)):
        return (
            f"postgresql://{urllib.parse.quote_plus(user)}:"
            f"{urllib.parse.quote_plus(password)}@{host}:{port}/{database}"
        )
    return _sanitize_db_url(get_secret("DATABASE_URL") or "")
