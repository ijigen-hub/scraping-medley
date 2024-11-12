file_path = "/Users/sunmeng/B_work/Ijigen/medley/scraping-medley/output/job_medley全職種求人.csv" 


with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()


new_file_path = file_path.replace(".csv", "_converted.csv")

with open(new_file_path, "w", encoding="utf-8-sig") as f:
    f.write(content)

print(f"転換されました：{new_file_path}")