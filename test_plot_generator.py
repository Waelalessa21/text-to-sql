import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "text_to_sql_engine" / "src"))

from ai_engine.core.plot_generator import PlotGenerator


def test_plot_generator():
    plot_gen = PlotGenerator(use_plotly=True)

    columns = ["department", "employee_count"]
    rows = [
        ["Engineering", 15],
        ["Sales", 10],
        ["Marketing", 8],
        ["HR", 5],
    ]

    print("=" * 60)
    print("Plot Generator Tests")
    print("=" * 60)

    test_cases = [
        ("Show me a bar chart of departments", "bar"),
        ("Plot employee count as a line chart", "line"),
        ("Create a pie chart of distribution", "pie"),
        ("Show histogram of salaries", "histogram"),
        ("Show data", None),
    ]

    for user_request, expected_type in test_cases:
        df, plot_code, error = plot_gen.generate(user_request, columns, rows)

        detected = plot_gen._detect_plot_type(user_request.lower())

        if plot_code:
            print(f"\nOK {user_request[:40]}")
            print(f"   Detected: {detected}")
            print(f"   Code length: {len(plot_code)} chars")
        elif error:
            print(f"\nDECLINED {user_request[:40]}")
            print(f"   Reason: {error}")
        else:
            print(f"\nNO PLOT {user_request[:40]}")

    print("\n" + "=" * 60)

    print("\nSample bar chart code:")
    print("-" * 60)
    df, plot_code, _ = plot_gen.generate("bar chart", columns, rows)
    if plot_code:
        print(plot_code)

    print("\n" + "=" * 60)
    print("All tests completed!")


if __name__ == "__main__":
    test_plot_generator()
