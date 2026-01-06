import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";
import fs from "fs/promises";

const execAsync = promisify(exec);

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { query, limit = 5, useApify = true } = body;

    if (!query) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 });
    }

    // Resolve paths from project root (assuming apps/web is CWD for Next.js, project root is ../..)
    const projectRoot = path.resolve(process.cwd(), "../../");
    const scriptPath = path.join(projectRoot, "skills/apollo-clay-leads/scripts/run_pipeline.py");
    // The script exports to ../output relative to the repo root (see scripts/export.py)
    const outputPath = path.resolve(projectRoot, "../output/leads.json");

    // Construct command
    const apifyFlag = useApify ? "--apify" : "";
    const command = `python3 "${scriptPath}" --query "${query.replace(/"/g, '\\"')}" --limit ${limit} ${apifyFlag}`;

    console.log("Executing:", command);
    
    // Execute script
    const { stdout, stderr } = await execAsync(command, { cwd: projectRoot });
    console.log("Python Script Output:", stdout);
    if (stderr) console.error("Python Script Errors:", stderr);

    // Read result
    try {
        const data = await fs.readFile(outputPath, "utf-8");
        const jsonData = JSON.parse(data);
        // The JSON file has structure: { run_id, stats, leads: [...] }
        // We need to return just the leads array
        return NextResponse.json({ success: true, leads: jsonData.leads || [] });
    } catch (readError) {
        console.error("Error reading output file:", readError);
        // Include script output in the error response for debugging
        return NextResponse.json({ 
            success: false, 
            error: "Pipeline ran but output file not found.", 
            details: stdout + "\n" + stderr 
        }, { status: 500 });
    }

  } catch (error: any) {
    console.error("Pipeline error:", error);
    return NextResponse.json({ success: false, error: error.message || "Internal Server Error" }, { status: 500 });
  }
}
