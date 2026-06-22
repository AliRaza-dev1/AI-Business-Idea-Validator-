import requests
import time
import json

print("=" * 60)
print("COMPLETE END-TO-END TEST")
print("=" * 60)

# 1. Create idea
print("\n1. Creating business idea...")
idea_resp = requests.post('http://localhost:8000/api/v1/ideas', json={
    'title': 'Mobile Payment App',
    'description': 'A fintech app for mobile payments',
    'problem_statement': 'People need easy mobile payments',
    'target_market': 'Consumers aged 18-40',
    'proposed_solution': 'Mobile payment platform',
    'value_proposition': 'Fast and secure payments',
    'business_model': 'Commission-based'
})

if idea_resp.status_code != 201:
    print(f"ERROR: {idea_resp.status_code}")
    print(idea_resp.text)
    exit(1)

idea = idea_resp.json()
idea_id = idea['id']
print(f"✓ Idea created with ID: {idea_id}")

# 2. Trigger analysis
print("\n2. Triggering analysis...")
analyze_resp = requests.post(f'http://localhost:8000/api/v1/analysis/{idea_id}/analyze')
print(f"✓ Analysis triggered (status: {analyze_resp.status_code})")

# 3. Wait for analysis to complete
print("\n3. Waiting for analysis to complete (max 20 seconds)...")
for i in range(10):
    time.sleep(2)
    check = requests.get(f'http://localhost:8000/api/v1/analysis/{idea_id}')
    if check.ok:
        data = check.json()
        score = data.get('overall_score', 'N/A')
        print(f"   ✓ Analysis complete! Score: {score}")
        break
    else:
        print(f"   Attempt {i+1}: Not ready yet...")
else:
    print("   ERROR: Analysis did not complete")
    exit(1)

# 4. Download PDF
print("\n4. Downloading PDF report...")
pdf_resp = requests.get(f'http://localhost:8000/api/v1/ideas/{idea_id}/report/pdf')

if pdf_resp.ok and len(pdf_resp.content) > 1000:
    print(f"✓ PDF downloaded successfully! Size: {len(pdf_resp.content)} bytes")
    
    # Save for verification
    with open('test_report_final.pdf', 'wb') as f:
        f.write(pdf_resp.content)
    print("✓ PDF saved to test_report_final.pdf")
    
    print("\n" + "=" * 60)
    print("✓ SUCCESS! All systems working correctly!")
    print("=" * 60)
    print("\n→ Go to http://localhost:3000 and test the web interface")
else:
    print(f"ERROR: PDF download failed")
    print(f"Status: {pdf_resp.status_code}")
    print(f"Size: {len(pdf_resp.content)}")
    print(f"Response: {pdf_resp.text[:200]}")
