"""
Process Open Food Facts Dataset
Filters nutraceuticals and creates 10K sample
(Download file manually first!)
"""

import pandas as pd
import os

# Paths
EXTERNAL_DRIVE = "/Volumes/My_backup/Data/STM_data"
FULL_DATASET_PATH = os.path.join(EXTERNAL_DRIVE, "full_dataset", "en.openfoodfacts.org.products.csv")
FILTERED_PATH = os.path.join(EXTERNAL_DRIVE, "filtered", "nutraceuticals_filtered.csv")
SAMPLE_PATH = "data/raw/nutraceuticals_10k_sample.csv"

print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║       OPEN FOOD FACTS DATASET PROCESSOR                  ║
║       Filter & Sample Nutraceuticals                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

# Create directories
print(f"\n📁 Creating directories...")
os.makedirs(os.path.join(EXTERNAL_DRIVE, "filtered"), exist_ok=True)
os.makedirs("data/raw", exist_ok=True)
print(f"✅ Directories ready!\n")

# Check if file exists
print("📥 Checking for dataset file...")
if not os.path.exists(FULL_DATASET_PATH):
    print(f"❌ Dataset file not found!")
    print(f"📍 Expected location: {FULL_DATASET_PATH}")
    print(f"\n💡 Please download manually:")
    print(f"   1. Go to: https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv")
    print(f"   2. Save to: {FULL_DATASET_PATH}")
    print(f"   3. Run this script again!")
    exit(1)

file_size = os.path.getsize(FULL_DATASET_PATH)
print(f"✅ Dataset found! ({file_size / (1024**3):.2f} GB)")

if file_size < 1 * (1024**3):  # Less than 1GB
    print(f"⚠️  WARNING: File seems small ({file_size / (1024**3):.2f} GB)")
    print(f"   Expected: 5-15 GB")
    print(f"   The download may be incomplete!")
    response = input("\n   Continue anyway? (yes/no): ")
    if response.lower() != 'yes':
        exit(1)

# Load and filter dataset
print("\n📊 STEP 1: Loading and filtering dataset in chunks...")
print("⏰ This might take 10-20 minutes (reading from external drive)...\n")

nutraceutical_keywords = [
    'vitamin', 'supplement', 'protein', 'omega', 'probiotic',
    'mineral', 'herbal', 'dietary-supplement', 'nutrition',
    'multivitamin', 'amino', 'creatine', 'bcaa', 'collagen',
    'energy-drink', 'sports-nutrition', 'meal-replacement'
]

# European + Asian markets
target_countries = [
    # Europe
    'Germany', 'France', 'United Kingdom', 'Spain', 'Italy',
    'Netherlands', 'Belgium', 'Austria', 'Switzerland', 'Poland',
    'Sweden', 'Denmark', 'Norway', 'Finland', 'Ireland',
    # Asia
    'China', 'Japan', 'South Korea', 'Singapore', 'Hong Kong',
    'Taiwan', 'Thailand', 'Malaysia', 'Indonesia', 'Vietnam',
    'India', 'Philippines'
]

keyword_pattern = '|'.join(nutraceutical_keywords)
country_pattern = '|'.join(target_countries)

CHUNK_SIZE = 50_000
filtered_chunks = []
total_rows = 0
chunk_num = 0
max_retries = 3

try:
    print("📖 Reading CSV in chunks of 50K rows (low memory usage)...")
    
    import csv
    reader = pd.read_csv(
        FULL_DATASET_PATH,
        sep='\t',
        on_bad_lines='skip',
        engine='c',
        quoting=csv.QUOTE_NONE,
        low_memory=False,
        chunksize=CHUNK_SIZE
    )
    
    for chunk in reader:
        chunk_num += 1
        total_rows += len(chunk)
        
        # Apply filters on each chunk
        mask = pd.Series([True] * len(chunk), index=chunk.index)
        
        if 'categories' in chunk.columns:
            mask = mask & chunk['categories'].notna()
            mask = mask & chunk['categories'].str.contains(keyword_pattern, case=False, na=False)
        
        if 'countries' in chunk.columns:
            mask = mask & chunk['countries'].notna()
            mask = mask & chunk['countries'].str.contains(country_pattern, case=False, na=False)
        
        if 'product_name' in chunk.columns:
            mask = mask & chunk['product_name'].notna()
        
        if 'energy-kcal_100g' in chunk.columns:
            mask = mask & chunk['energy-kcal_100g'].notna()
        elif 'energy_100g' in chunk.columns:
            mask = mask & chunk['energy_100g'].notna()
        
        matched = chunk[mask]
        if len(matched) > 0:
            filtered_chunks.append(matched)
        
        found_so_far = sum(len(c) for c in filtered_chunks)
        print(f"   Chunk {chunk_num}: processed {total_rows:,} rows | found {found_so_far:,} matches so far", flush=True)
    
    print(f"\n✅ Finished reading {total_rows:,} total products")
    
    if filtered_chunks:
        filtered_df = pd.concat(filtered_chunks, ignore_index=True)
    else:
        filtered_df = pd.DataFrame()
    
    print(f"✅ Found {len(filtered_df):,} European nutraceutical products!\n")
    
    # Save filtered dataset
    print(f"💾 Saving filtered dataset to external drive...")
    filtered_df.to_csv(FILTERED_PATH, index=False)
    print(f"✅ Saved to: {FILTERED_PATH}\n")

except Exception as e:
    # If we got some data before the error, save what we have
    if filtered_chunks:
        filtered_df = pd.concat(filtered_chunks, ignore_index=True)
        print(f"\n⚠️  Error after processing {total_rows:,} rows: {e}")
        print(f"💾 Saving {len(filtered_df):,} products found so far...")
        filtered_df.to_csv(FILTERED_PATH, index=False)
        print(f"✅ Partial results saved to: {FILTERED_PATH}")
    else:
        print(f"❌ Error processing dataset: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

# Create stratified sample
print("\n🎯 STEP 2: Creating stratified sample...")

try:
    # Get main category
    filtered_df['main_category'] = filtered_df['categories'].str.split(',').str[0]
    
    # Count products per category
    category_counts = filtered_df['main_category'].value_counts()
    print(f"\n📊 Found {len(category_counts)} categories")
    print("\nTop 10 categories:")
    print(category_counts.head(10))
    
    # Sample products (up to 10,000)
    sample_size = min(10000, len(filtered_df))
    
    if len(filtered_df) <= sample_size:
        # Use all products if we have less than 10K
        sample_df = filtered_df.copy()
        print(f"\n✅ Using all {len(sample_df):,} products (less than 10K available)\n")
    else:
        # Stratified sampling
        samples_per_category = (category_counts / category_counts.sum() * sample_size).astype(int)
        
        sampled_products = []
        for category, n_samples in samples_per_category.items():
            if n_samples > 0:
                category_products = filtered_df[filtered_df['main_category'] == category]
                n_samples = min(n_samples, len(category_products))
                sample = category_products.sample(n=n_samples, random_state=42)
                sampled_products.append(sample)
        
        sample_df = pd.concat(sampled_products, ignore_index=True)
        print(f"\n✅ Created sample with {len(sample_df):,} products\n")
    
    # Select relevant columns
    relevant_columns = [
        'code', 'product_name', 'brands', 'categories', 'countries',
        'energy-kcal_100g', 'fat_100g', 'saturated-fat_100g',
        'carbohydrates_100g', 'sugars_100g', 'proteins_100g',
        'salt_100g', 'fiber_100g',
        'image_url', 'image_front_url', 'image_nutrition_url'
    ]
    
    available_columns = [col for col in relevant_columns if col in sample_df.columns]
    clean_sample = sample_df[available_columns].copy()
    
    # Rename for STM
    rename_map = {
        'product_name': 'name',
        'brands': 'brand',
        'energy-kcal_100g': 'energy_kcal',
        'fat_100g': 'fat',
        'saturated-fat_100g': 'saturated_fat',
        'carbohydrates_100g': 'carbohydrates',
        'sugars_100g': 'sugar',
        'proteins_100g': 'protein',
        'salt_100g': 'salt',
        'fiber_100g': 'fiber'
    }
    
    clean_sample = clean_sample.rename(columns=rename_map)
    
    # Save to Mac
    print(f"💾 Saving sample to Mac for analysis...")
    clean_sample.to_csv(SAMPLE_PATH, index=False)
    print(f"✅ Saved to: {SAMPLE_PATH}\n")
    
except Exception as e:
    print(f"❌ Error creating sample: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Summary
print("\n" + "="*70)
print("🎉 DATASET PROCESSING COMPLETE!")
print("="*70)
print(f"\n📊 SUMMARY:")
print(f"   Total products in dataset:    {total_rows:,}")
print(f"   European nutraceuticals:      {len(filtered_df):,}")
print(f"   Sample for analysis:          {len(clean_sample):,}")
print(f"\n💾 FILES SAVED:")
print(f"   📦 Full dataset:              {FULL_DATASET_PATH}")
print(f"      Size: {os.path.getsize(FULL_DATASET_PATH) / (1024**3):.2f} GB")
print(f"   🔍 Filtered dataset:          {FILTERED_PATH}")
print(f"   🎯 Sample for STM:            {SAMPLE_PATH}")
print(f"\n🚀 NEXT STEPS:")
print(f"   1. Build the web dashboard!")
print(f"   2. Analyze the sample with STM")
print(f"   3. Show your guide!")
print(f"\n🎓 Your thesis is going to be AMAZING! 💪\n")