import argparse
import json
import tool
from utils import format_diagnostic_report

def main():
    parser = argparse.ArgumentParser(description="IntelliHub MCP Tool CLI")
    sub = parser.add_subparsers(dest="command")

    # list_files
    sub.add_parser("list", help="List all files in ai_context")

    # read_file
    read = sub.add_parser("read", help="Read a file by relative path")
    read.add_argument("path", type=str)

    # search
    search = sub.add_parser("search", help="Search for a term")
    search.add_argument("query", type=str)

    # get_schema
    schema = sub.add_parser("schema", help="Get a schema by name")
    schema.add_argument("name", type=str)

    # get_module_purpose
    mp = sub.add_parser("module", help="Get a module purpose by name")
    mp.add_argument("name", type=str)

    # diagnose
    sub.add_parser("diagnose", help="Run a full diagnostic report")

    args = parser.parse_args()

    if args.command == "list":
        print("\n".join(tool.list_files()))

    elif args.command == "read":
        print(tool.read_file(args.path))

    elif args.command == "search":
        results = tool.search(args.query)
        print(json.dumps(results, indent=2))

    elif args.command == "schema":
        print(tool.get_schema(args.name))

    elif args.command == "module":
        print(tool.get_module_purpose(args.name))

    elif args.command == "diagnose":
        report = tool.diagnose()
        print(format_diagnostic_report(report))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
