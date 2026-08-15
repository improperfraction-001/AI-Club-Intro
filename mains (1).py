
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "crashes.csv"

# Date formats the user is allowed to type for an exact-date search
DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"]



def load_crashes(path=DATA_FILE):
    
    crashes = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["date"] = datetime.strptime(row["date"], "%Y-%m-%d").date()
            row["aboard"] = int(row["aboard"])
            row["fatalities"] = int(row["fatalities"])
            crashes.append(row)
    return crashes



# All text searches are case-insensitive substring matches, so
# "air india" matches both Air India and Air India Express,
# and "engine" matches "engine failure".

def search_airline(crashes, query):
    q = query.strip().lower()
    return [c for c in crashes if q in c["airline"].lower()]


def search_aircraft(crashes, query):
    q = query.strip().lower()
    return [c for c in crashes if q in c["aircraft"].lower()]


def search_cause(crashes, query):
    q = query.strip().lower()
    return [c for c in crashes if q in c["cause"].lower()]


def search_year(crashes, year):
    return [c for c in crashes if c["date"].year == year]


def search_date(crashes, when):
    return [c for c in crashes if c["date"] == when]


def parse_date(text):
    """Try a handful of common date formats. Returns a date, or None."""
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None



def show_results(results):
    if not results:
        print("\n  No crashes found for that search.\n")
        return
    results = sorted(results, key=lambda c: c["date"])
    print()
    for i, c in enumerate(results, 1):
        flight = f" {c['flight']}" if c["flight"] else ""
        print(f"{i}. {c['date'].isoformat()}  |  {c['airline']}{flight}  |  {c['aircraft']}")
        print(f"   {c['location']}  |  {c['fatalities']} of {c['aboard']} aboard killed")
        print(f"   Cause: {c['cause']}")
        print(f"   {c['summary']}")
        print()
    total = sum(c["fatalities"] for c in results)
    print(f"  -> {len(results)} crash(es) found, {total} deaths in total\n")


def show_causes(crashes):
    counts = Counter(c["cause"] for c in crashes)
    print("\nCause categories in the database:")
    for cause, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {cause:<32} {n}")
    print()


def show_stats(crashes):
    years = [c["date"].year for c in crashes]
    deadliest = max(crashes, key=lambda c: c["fatalities"])
    top_causes = Counter(c["cause"] for c in crashes).most_common(3)
    print(f"\n  Crashes in database : {len(crashes)}")
    print(f"  Years covered       : {min(years)} - {max(years)}")
    print(f"  Total deaths aboard : {sum(c['fatalities'] for c in crashes)}")
    print(f"  Deadliest crash     : {deadliest['airline']} {deadliest['flight']} "
          f"({deadliest['date'].isoformat()}), {deadliest['fatalities']} killed")
    causes = ", ".join(f"{cause} ({n})" for cause, n in top_causes)
    print(f"  Most common causes  : {causes}\n")



MENU = """
==========  AIRPLANE CRASH EXPLORER  ==========
 1) Search by airline
 2) Search by year
 3) Search by exact date
 4) Search by aircraft type
 5) Search by cause / failure type
 6) List cause categories
 7) Database stats
 0) Quit
"""


def main():
    try:
        crashes = load_crashes()
    except FileNotFoundError:
        print(f"Could not find {DATA_FILE}. Keep crashes.csv next to main.py.")
        return

    years = [c["date"].year for c in crashes]
    print(f"\nLoaded {len(crashes)} notable crashes ({min(years)}-{max(years)}).")
    print("Curated educational sample - not a complete accident record.")

    while True:
        print(MENU)
        choice = input("Pick an option: ").strip()

        if choice == "0":
            print("Bye.")
            break

        elif choice == "1":
            q = input("Airline name (or part of it): ")
            if not q.strip():
                print("Type at least one character.")
                continue
            show_results(search_airline(crashes, q))

        elif choice == "2":
            q = input("Year (e.g. 1985): ").strip()
            if not q.isdigit():
                print("Please enter a 4-digit year.")
                continue
            show_results(search_year(crashes, int(q)))

        elif choice == "3":
            q = input("Date (e.g. 1977-03-27 or 27-03-1977): ").strip()
            when = parse_date(q)
            if when is not None:
                show_results(search_date(crashes, when))
            elif q.isdigit() and len(q) == 4:
                
                show_results(search_year(crashes, int(q)))
            else:
                print("Couldn't read that date. Try formats like 1977-03-27, "
                      "27-03-1977, or 27 March 1977.")

        elif choice == "4":
            q = input("Aircraft type (e.g. 737, A320, DC-10): ")
            if not q.strip():
                print("Type at least one character.")
                continue
            show_results(search_aircraft(crashes, q))

        elif choice == "5":
            q = input("Cause / failure type (e.g. engine, fire, bird): ")
            if not q.strip():
                print("Type at least one character. Option 6 lists all categories.")
                continue
            show_results(search_cause(crashes, q))

        elif choice == "6":
            show_causes(crashes)

        elif choice == "7":
            show_stats(crashes)

        else:
            print("Please pick a number from 0 to 7.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBye.")
