#fetch_trial.py
import requests
import pandas as pd
import json


def parse_v2_json(raw_json):
    """Parse ClinicalTrials.gov v2 JSON structure into a flat DataFrame (safe version)."""
    import json
    if isinstance(raw_json, str):
        try:
            raw_json = json.loads(raw_json)
        except Exception:
            print(" Could not parse JSON string.")
            return pd.DataFrame()

    if not isinstance(raw_json, dict):
        print(" Unexpected response type.")
        return pd.DataFrame()

    studies = raw_json.get("studies", [])
    if not isinstance(studies, list) or not studies:
        print(" No valid studies found.")
        return pd.DataFrame()

    extracted = []
    for s in studies:
        if not isinstance(s, dict):
            continue

        ps = s.get("protocolSection", {})
        if not isinstance(ps, dict):
            continue

        idm = ps.get("identificationModule", {}) if isinstance(ps.get("identificationModule"), dict) else {}
        cond = ps.get("conditionsModule", {}) if isinstance(ps.get("conditionsModule"), dict) else {}
        loc = ps.get("contactsLocationsModule", {}) if isinstance(ps.get("contactsLocationsModule"), dict) else {}
        des = ps.get("designModule", {}) if isinstance(ps.get("designModule"), dict) else {}
        stat = ps.get("statusModule", {}) if isinstance(ps.get("statusModule"), dict) else {}

        condition_list = cond.get("conditions", [])
        if isinstance(condition_list, list):
            condition = ", ".join(map(str, condition_list))
        else:
            condition = condition_list

        location_list = loc.get("locations", [])
        loc_names = []
        if isinstance(location_list, list):
            for item in location_list:
                if isinstance(item, dict):
                    facility = item.get("facility", {})
                    if isinstance(facility, dict):
                        name = facility.get("name")
                        if name:
                            loc_names.append(name)
                elif isinstance(item, str):
                    loc_names.append(item)
        location_str = ", ".join(loc_names) if loc_names else None

        extracted.append({
            "NCTId": idm.get("nctId"),
            "BriefTitle": idm.get("briefTitle"),
            "Condition": condition,
            "EnrollmentCount": des.get("enrollmentInfo", {}).get("count") if isinstance(des.get("enrollmentInfo"), dict) else None,
            "StartDate": stat.get("startDateStruct", {}).get("date") if isinstance(stat.get("startDateStruct"), dict) else None,
            "LastUpdatePostDate": stat.get("lastUpdatePostDateStruct", {}).get("date") if isinstance(stat.get("lastUpdatePostDateStruct"), dict) else None,
            "Location": location_str,
            "LeadSponsorName": ps.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name")
                if isinstance(ps.get("sponsorCollaboratorsModule", {}).get("leadSponsor"), dict) else None,
            "OverallStatus": stat.get("overallStatus"),
            "StudyType": des.get("studyType"),
        })

    df = pd.DataFrame(extracted)
    return df
def get_trials_v2(term, page_size):
    """Fetch study data from ClinicalTrials.gov v2 API."""
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {"query.term": term, "pageSize": page_size}

    resp = requests.get(url, params=params, timeout=15)
    print(f"🔍 Response status: {resp.status_code}")
    print(f"🔍 Content-Type: {resp.headers.get('Content-Type')}")
    print(f"🔍 First 200 chars: {resp.text[:200]}")
    resp.raise_for_status()

    data = resp.json()
    return parse_v2_json(data)


def get_trials(term, page_size):
    try:
        df = get_trials_v2(term, page_size)
        if len(df) == 0:
            raise ValueError("v2 returned empty data.")
        print(f"Fetched {len(df)} trials via v2 API")
        return df
    except Exception as e:
        print(f" v2 API failed: {e}")
        return pd.DataFrame()
