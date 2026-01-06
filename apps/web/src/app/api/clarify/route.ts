import { NextRequest, NextResponse } from "next/server";

/**
 * API endpoint to assess if a query needs clarification
 * before running the lead search pipeline.
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { query } = body;

    if (!query) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 });
    }

    // Call Python clarification script
    const { spawn } = await import("child_process");
    const path = await import("path");

    const projectRoot = path.resolve(process.cwd(), "../../");
    const scriptPath = path.join(
      projectRoot,
      "skills/apollo-clay-leads/scripts/clarify_query.py"
    );

    return new Promise((resolve) => {
      const pythonProcess = spawn("python3", [scriptPath, query], {
        cwd: projectRoot,
      });

      let stdout = "";
      let stderr = "";

      pythonProcess.stdout.on("data", (data: Buffer) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on("data", (data: Buffer) => {
        stderr += data.toString();
      });

      pythonProcess.on("close", (code) => {
        if (code !== 0) {
          console.error("Clarify script error:", stderr);
          resolve(
            NextResponse.json(
              { needs_clarification: false, error: "Script failed" },
              { status: 200 }
            )
          );
          return;
        }

        try {
          const result = JSON.parse(stdout);
          resolve(NextResponse.json(result));
        } catch (e) {
          console.error("Failed to parse clarify output:", stdout);
          resolve(
            NextResponse.json(
              { needs_clarification: false, error: "Parse error" },
              { status: 200 }
            )
          );
        }
      });
    });
  } catch (error: any) {
    console.error("Clarify API error:", error);
    return NextResponse.json(
      { needs_clarification: false, error: error.message },
      { status: 200 }
    );
  }
}
