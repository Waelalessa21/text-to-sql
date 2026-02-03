from typing import Any, List, Optional, Tuple

import pandas as pd


class PlotGenerator:
    DECLINE_MESSAGE = "Cannot generate plot: insufficient data or incompatible request."

    def __init__(self, use_plotly: bool = True):
        self.use_plotly = use_plotly

    def generate(
        self,
        user_request: str,
        columns: List[str],
        rows: List[List],
        plot_type: Optional[str] = None,
    ) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
        if not rows or not columns:
            return None, None, self.DECLINE_MESSAGE

        df = pd.DataFrame(rows, columns=columns)

        if df.empty:
            return df, None, self.DECLINE_MESSAGE

        # Use provided plot_type, or try to detect from user_request
        if plot_type is None:
            plot_type = self._detect_plot_type(user_request.lower())
            if plot_type is None:
                return (
                    df,
                    None,
                    "Could not detect plot type from request. Please select a specific plot type.",
                )

        plot_code = self._generate_plot_code(df, plot_type, user_request)

        if plot_code is None:
            return df, None, self.DECLINE_MESSAGE

        return df, plot_code, None

    def get_figure(
        self,
        user_request: str,
        columns: List[str],
        rows: List[List],
        plot_type: Optional[str] = None,
    ) -> Tuple[Optional[Any], Optional[str]]:
        """Build and return the plotly figure (for export to image). Returns (fig, None) or (None, error_message)."""
        df, plot_code, plot_err = self.generate(
            user_request, columns, rows, plot_type=plot_type
        )
        if plot_err or not plot_code or df is None:
            return None, plot_err or self.DECLINE_MESSAGE
        if not self.use_plotly:
            return None, "Image export is only supported for Plotly charts."
        try:
            import plotly.express as px

            exec_globals: dict = {"df": df, "px": px}
            exec(plot_code, exec_globals)
            fig = exec_globals.get("fig")
            return (fig, None) if fig is not None else (None, "Figure was not created.")
        except Exception as e:
            return None, str(e)

    def get_figure_as_png(
        self,
        user_request: str,
        columns: List[str],
        rows: List[List],
        plot_type: Optional[str] = None,
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """Build chart and return PNG bytes. Returns (png_bytes, None) or (None, error_message)."""
        fig, err = self.get_figure(user_request, columns, rows, plot_type=plot_type)
        if err or fig is None:
            return None, err or self.DECLINE_MESSAGE
        try:
            png_bytes = fig.to_image(format="png")
            return png_bytes, None
        except Exception as e:
            return None, str(e)

    def _detect_plot_type(self, user_request: str) -> Optional[str]:
        plot_keywords = {
            "bar": ["bar", "column", "vertical"],
            "line": ["line", "trend", "time series", "over time"],
            "scatter": ["scatter", "correlation", "relationship", "vs"],
            "pie": ["pie", "distribution", "percentage", "proportion"],
            "histogram": ["histogram", "frequency", "distribution"],
        }

        # Check if the request itself is a plot type name
        user_request_lower = user_request.lower().strip()
        if user_request_lower in plot_keywords:
            return user_request_lower

        # Check for keywords
        for plot_type, keywords in plot_keywords.items():
            if any(keyword in user_request for keyword in keywords):
                return plot_type

        return None

    def _generate_plot_code(
        self, df: pd.DataFrame, plot_type: str, user_request: str
    ) -> Optional[str]:
        if self.use_plotly:
            return self._generate_plotly_code(df, plot_type)
        else:
            return self._generate_matplotlib_code(df, plot_type)

    def _generate_plotly_code(self, df: pd.DataFrame, plot_type: str) -> Optional[str]:
        cols = df.columns.tolist()

        if len(cols) < 2 and plot_type != "histogram":
            return None

        if plot_type == "bar":
            x_col = cols[0]
            y_col = cols[1] if len(cols) > 1 else cols[0]
            code = f"""fig = px.bar(df, x='{x_col}', y='{y_col}', title='Bar Chart')
fig.show()"""
            return code

        elif plot_type == "line":
            x_col = cols[0]
            y_col = cols[1] if len(cols) > 1 else cols[0]
            code = f"""fig = px.line(df, x='{x_col}', y='{y_col}', title='Line Chart', markers=True)
fig.show()"""
            return code

        elif plot_type == "scatter":
            if len(cols) < 2:
                return None
            x_col = cols[0]
            y_col = cols[1]
            code = f"""fig = px.scatter(df, x='{x_col}', y='{y_col}', title='Scatter Plot')
fig.show()"""
            return code

        elif plot_type == "pie":
            names_col = cols[0]
            values_col = cols[1] if len(cols) > 1 else cols[0]
            code = f"""fig = px.pie(df, names='{names_col}', values='{values_col}', title='Pie Chart')
fig.show()"""
            return code

        elif plot_type == "histogram":
            col = cols[0]
            code = f"""fig = px.histogram(df, x='{col}', title='Histogram')
fig.show()"""
            return code

        return None

    def _generate_matplotlib_code(
        self, df: pd.DataFrame, plot_type: str
    ) -> Optional[str]:
        cols = df.columns.tolist()

        if len(cols) < 2 and plot_type not in ["histogram", "pie"]:
            return None

        if plot_type == "bar":
            x_col = cols[0]
            y_col = cols[1] if len(cols) > 1 else cols[0]
            code = f"""import matplotlib.pyplot as plt

df.plot(kind='bar', x='{x_col}', y='{y_col}', legend=False)
plt.title('Bar Chart')
plt.xlabel('{x_col}')
plt.ylabel('{y_col}')
plt.tight_layout()
plt.show()"""
            return code

        elif plot_type == "line":
            x_col = cols[0]
            y_col = cols[1] if len(cols) > 1 else cols[0]
            code = f"""import matplotlib.pyplot as plt

df.plot(kind='line', x='{x_col}', y='{y_col}', marker='o', legend=False)
plt.title('Line Chart')
plt.xlabel('{x_col}')
plt.ylabel('{y_col}')
plt.tight_layout()
plt.show()"""
            return code

        elif plot_type == "scatter":
            if len(cols) < 2:
                return None
            x_col = cols[0]
            y_col = cols[1]
            code = f"""import matplotlib.pyplot as plt

plt.scatter(df['{x_col}'], df['{y_col}'])
plt.title('Scatter Plot')
plt.xlabel('{x_col}')
plt.ylabel('{y_col}')
plt.tight_layout()
plt.show()"""
            return code

        elif plot_type == "pie":
            if len(cols) < 2:
                return None
            labels_col = cols[0]
            values_col = cols[1]
            code = f"""import matplotlib.pyplot as plt

plt.pie(df['{values_col}'], labels=df['{labels_col}'], autopct='%1.1f%%')
plt.title('Pie Chart')
plt.tight_layout()
plt.show()"""
            return code

        elif plot_type == "histogram":
            col = cols[0]
            code = f"""import matplotlib.pyplot as plt

df['{col}'].hist(bins=20)
plt.title('Histogram')
plt.xlabel('{col}')
plt.ylabel('Frequency')
plt.tight_layout()
plt.show()"""
            return code

        return None
