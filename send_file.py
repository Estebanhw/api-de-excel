import os
import sys
try:
    import requests
except ImportError:
    requests = None

URL = "http://127.0.0.1:8000/process"
INPUT = "sample_input.xlsx"
OUTPUT = "sample_output.xlsx"

if not os.path.exists(INPUT):
    print("Input file not found:", INPUT)
    sys.exit(1)

if requests:
    with open(INPUT, "rb") as f:
        r = requests.post(URL, files={"file": (INPUT, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    if r.status_code == 200:
        with open(OUTPUT, "wb") as out:
            out.write(r.content)
        print("WROTE", OUTPUT)
    else:
        print("Request failed", r.status_code, r.text)
else:
    # Fallback: use urllib
    import mimetypes
    from urllib import request

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    def encode_multipart(filename, fieldname="file"):
        with open(filename, "rb") as f:
            filedata = f.read()
        mime = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        lines = []
        lines.append(f"--{boundary}")
        lines.append(f'Content-Disposition: form-data; name="{fieldname}"; filename="{os.path.basename(filename)}"')
        lines.append(f"Content-Type: {mime}")
        lines.append("")
        body_pre = "\r\n".join(lines).encode('utf-8') + b"\r\n"
        body_post = f"\r\n--{boundary}--\r\n".encode('utf-8')
        return body_pre + filedata + body_post

    data = encode_multipart(INPUT)
    req = request.Request(URL, data=data)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req.add_header('Content-Length', str(len(data)))
    try:
        resp = request.urlopen(req)
        out = resp.read()
        with open(OUTPUT, 'wb') as f:
            f.write(out)
        print('WROTE', OUTPUT)
    except Exception as e:
        print('Request failed', e)
