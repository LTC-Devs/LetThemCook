import { NextResponse, connection } from "next/server";

export async function GET() {
	// Disable caching
	await connection();

	try {
		return NextResponse.json(
			{ status: "ok", timestamp: new Date().toISOString() },
			{ status: 200 }
		);
	} catch (error: any) {
		return NextResponse.json(
			{ status: "unhealthy", error: error.message },
			{ status: 503 }
		);
	}
}
