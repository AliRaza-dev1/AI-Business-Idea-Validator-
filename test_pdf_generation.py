#!/usr/bin/env python
"""Test PDF generation end-to-end"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001/api/v1"

def test_pdf_generation():
    """Test the complete PDF generation flow"""
    
    # 1. Create an idea
    print("1. Creating test idea...")
    idea_data = {
        "title": "AI Resume Builder",
        "description": "An AI-powered platform that helps users create professional resumes",
        "problem_statement": "Job seekers struggle to create effective resumes",
        "target_market": "College graduates and job seekers",
        "proposed_solution": "AI-powered resume builder with suggestions",
        "value_proposition": "Professional resumes in minutes with AI assistance",
        "business_model": "Freemium SaaS"
    }
    
    resp = requests.post(f'{BASE_URL}/ideas', json=idea_data)
    if resp.status_code != 201:
        print(f"✗ Failed to create idea: {resp.status_code}")
        print(f"  Response: {resp.text}")
        return False
        
    idea_id = resp.json()['id']
    print(f"✓ Idea created with ID: {idea_id}")
    
    # 2. Trigger analysis
    print("\n2. Triggering analysis...")
    resp = requests.post(f'{BASE_URL}/analysis/{idea_id}/analyze')
    if resp.status_code != 202:
        print(f"✗ Failed to trigger analysis: {resp.status_code}")
        print(f"  Response: {resp.text}")
        return False
    print(f"✓ Analysis triggered (status: {resp.status_code})")
    
    # 3. Wait for analysis to complete
    print("\n3. Waiting for analysis to complete (max 30 seconds)...")
    for i in range(15):
        time.sleep(2)
        resp = requests.get(f'{BASE_URL}/analysis/{idea_id}')
        if resp.ok:
            data = resp.json()
            print(f"✓ Analysis complete! Overall score: {data.get('overall_score')}")
            break
        else:
            print(f"  Attempt {i+1}: Analysis not ready (status {resp.status_code})")
    else:
        print("✗ Analysis did not complete in time")
        return False
    
    # 4. Test PDF download
    print("\n4. Testing PDF download...")
    resp = requests.get(f'{BASE_URL}/ideas/{idea_id}/report/pdf')
    if resp.ok:
        pdf_size = len(resp.content)
        print(f"✓ PDF generated successfully! Size: {pdf_size} bytes")
        
        # Save PDF to verify
        pdf_path = 'test_report.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(resp.content)
        print(f"✓ PDF saved to {pdf_path}")
        return True
    else:
        print(f"✗ PDF generation failed: {resp.status_code}")
        print(f"  Response: {resp.text[:500]}")
        return False

if __name__ == '__main__':
    try:
        success = test_pdf_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
