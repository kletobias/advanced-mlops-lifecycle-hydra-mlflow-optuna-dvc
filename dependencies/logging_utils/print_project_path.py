def print_project_path(path: str) -> str:
    if path.startswith("/Users/tobias"):
        return path.replace(
            "/Users/tobias/.local/projects/portfolio_medical_drg_ny/",
            "",
        )
    return None
