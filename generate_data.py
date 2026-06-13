import pandas as pd
import numpy as np

np.random.seed(42)

states_districts = {
    "Uttar Pradesh": ["Gorakhpur", "Varanasi", "Lucknow", "Agra", "Meerut", "Allahabad", "Bareilly", "Aligarh", "Moradabad", "Saharanpur"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga", "Araria", "Sitamarhi", "Madhubani", "Supaul", "Kishanganj"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Sagar", "Rewa", "Satna", "Singrauli", "Shahdol", "Umaria"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Barmer", "Jaisalmer", "Banswara", "Dungarpur", "Pratapgarh", "Sirohi"],
    "Jharkhand": ["Ranchi", "Dhanbad", "Bokaro", "Deoghar", "Pakur", "Godda", "Sahibganj", "Dumka", "Giridih", "Hazaribagh"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Berhampur", "Rayagada", "Koraput", "Malkangiri", "Nabarangpur", "Nuapada", "Bolangir", "Kalahandi"],
    "West Bengal": ["Kolkata", "Howrah", "Murshidabad", "Malda", "Purulia", "Bankura", "Birbhum", "Cooch Behar", "Jalpaiguri", "Darjeeling"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Nandurbar", "Gadchiroli", "Washim", "Yavatmal", "Osmanabad", "Hingoli"],
}

rows = []
for state, districts in states_districts.items():
    for district in districts:
        eligible_farmers = np.random.randint(80000, 500000)

        # Base socio-economic factors first
        literacy_rate = round(np.random.uniform(45, 85), 1)
        bank_branch_per_lakh = round(np.random.uniform(4, 28), 1)
        internet_penetration = round(np.random.uniform(18, 72), 1)
        asha_worker_coverage = round(np.random.uniform(55, 98), 1)
        female_farmer_pct = round(np.random.uniform(12, 48), 1)
        avg_landholding_acres = round(np.random.uniform(0.8, 4.5), 2)

        # Uptake NOW driven by these factors (realistic relationship)
        base_uptake = (
            0.35 * literacy_rate +
            0.50 * bank_branch_per_lakh +
            0.10 * internet_penetration +
            0.08 * asha_worker_coverage
        )
        # Normalize to 20-90% range
        base_uptake = (base_uptake - base_uptake * 0.6) 
        noise = np.random.normal(0, 4)
        uptake_pct = round(np.clip(20 + (literacy_rate - 45) * 0.4 + 
                                   (bank_branch_per_lakh - 4) * 1.2 + 
                                   noise, 18, 91), 2)

        # Force bottom 10 districts low
        if district in ["Araria", "Sitamarhi", "Koraput", "Malkangiri", 
                        "Pakur", "Godda", "Barmer", "Dungarpur", "Nuapada", "Kalahandi"]:
            uptake_pct = round(np.random.uniform(18, 35), 2)
            literacy_rate = round(np.random.uniform(45, 58), 1)
            bank_branch_per_lakh = round(np.random.uniform(4, 12), 1)

        enrolled_farmers = int(eligible_farmers * uptake_pct / 100)
        gap_farmers = eligible_farmers - enrolled_farmers

        rows.append({
            "State": state,
            "District": district,
            "Eligible_Farmers": eligible_farmers,
            "Enrolled_Farmers": enrolled_farmers,
            "Uptake_Pct": uptake_pct,
            "Gap_Farmers": gap_farmers,
            "Literacy_Rate": literacy_rate,
            "Internet_Penetration": internet_penetration,
            "Female_Farmer_Pct": female_farmer_pct,
            "Avg_Landholding_Acres": avg_landholding_acres,
            "Bank_Branch_Per_Lakh": bank_branch_per_lakh,
            "ASHA_Worker_Coverage": asha_worker_coverage,
        })

df = pd.DataFrame(rows)
df.to_csv("pmkisan_data.csv", index=False)
print(" Dataset regenerated!")
print(f"Total districts: {len(df)}")
print(f"\nBottom 10 districts:")
print(df.nsmallest(10, 'Uptake_Pct')[['District','State','Uptake_Pct','Gap_Farmers']].to_string(index=False))

# Print correlations to verify
from scipy import stats
print("\nCorrelations with Uptake (should be significant now):")
for col in ['Literacy_Rate','Bank_Branch_Per_Lakh','Internet_Penetration','ASHA_Worker_Coverage']:
    r, p = stats.pearsonr(df[col], df['Uptake_Pct'])
    sig = " Significant" if p < 0.05 else "❌ Weak"
    print(f"  {col:<30} r={r:+.2f}  p={p:.3f}  {sig}")