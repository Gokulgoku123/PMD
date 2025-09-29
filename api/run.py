import subprocess
import tempfile
import json

# Vercel serverless handler
def handler(request):
    try:
        # Read request body
        body = request.body.read().decode("utf-8") if request.body else "{}"
        data = json.loads(body or "{}")

        classes = data.get("classes", [])  # Expecting list of {"name":..., "source":...}
        combined_violations = []
        warnings_list = []

        for cls in classes:
            name = cls.get("name", "UnknownClass")
            source_code = cls.get("source", "")

            # Write source to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".cls", mode="w", encoding="utf-8") as tmp:
                tmp.write(source_code)
                tmp_path = tmp.name

            # Run PMD CLI
            try:
                result = subprocess.run(
                    [
                        "java",
                        "-cp",
                        "/opt/pmd/lib/*",
                        "net.sourceforge.pmd.PMD",
                        "-d",
                        tmp_path,
                        "-R",
                        "rulesets/java/quickstart.xml",
                        "-f",
                        "json"
                    ],
                    capture_output=True,
                    text=True
                )

                # Parse output JSON if possible
                if result.stdout:
                    parsed = json.loads(result.stdout)
                    files = parsed.get("files", [])
                    for f in files:
                        for v in f.get("violations", []):
                            v["className"] = name
                            combined_violations.append(v)

                if result.stderr:
                    warnings_list.append(f"Class {name}: {result.stderr.strip()}")

            except Exception as e:
                combined_violations.append({"parseError": str(e), "className": name})

        # Return combined PMD results
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "violations": combined_violations,
                "warnings": warnings_list
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
