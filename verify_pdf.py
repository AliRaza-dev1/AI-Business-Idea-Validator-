import requests

pdf = requests.get('http://localhost:8000/api/v1/ideas/126/report/pdf')
print("Status:", pdf.status_code)
print("Size:", len(pdf.content), "bytes")

if len(pdf.content) > 1000 and pdf.content.startswith(b'%PDF'):
    print("✓ SUCCESS: Valid PDF generated!")
else:
    print("Content preview:", pdf.text[:200])
