import requests


def log(*msg):
    import photon

    print(*msg)
    webhook_url = photon.config.get("audit_webhook")
    if not webhook_url:
        return
    requests.post(
        webhook_url,
        json={
            "content": " ".join(str(m) for m in msg),
        },
    )


if __name__ == "__main__":
    import sys

    log(*sys.argv[1:])
