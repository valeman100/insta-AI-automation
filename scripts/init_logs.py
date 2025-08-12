from pathlib import Path


def ensure_logs_csv_exists(repo_root: Path) -> None:
    logs_path = repo_root / "logs.csv"
    if logs_path.exists():
        return
    header = (
        "main_title,subtitle,post_caption,hashtags,json,date,"
        "edited_img_path,published,image_prompt\n"
    )
    logs_path.write_text(header, encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    ensure_logs_csv_exists(root)
    print(f"Initialized {root / 'logs.csv'}")


