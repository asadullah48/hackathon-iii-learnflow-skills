#!/usr/bin/env node
try {
    eval(process.argv[2] || "");
} catch (e) {
    console.error("Error:", e.message);
    process.exit(1);
}
