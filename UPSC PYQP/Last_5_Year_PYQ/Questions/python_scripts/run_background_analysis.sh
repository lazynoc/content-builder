#!/bin/bash

# Background Grok Analysis Runner
# This script runs the UPSC Grok analysis in the background

echo "🚀 Starting Background Grok Analysis for UPSC 2025 & 2024"
echo "=================================================="

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Check if the analysis script exists
if [ ! -f "grok_analysis_background_agent.py" ]; then
    echo "❌ grok_analysis_background_agent.py not found"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Get current timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Run the background analysis
echo "📝 Starting analysis at $(date)"
echo "📁 Log file: logs/grok_analysis_${TIMESTAMP}.log"
echo "⏱️  Estimated time: 60-90 minutes for both years"
echo "💰 Estimated cost: ~$720 (vs ~$3,600 individual processing)"
echo ""
echo "🔄 Running in background... (Ctrl+C to stop)"
echo ""

# Run the analysis in background with logging
nohup python3 grok_analysis_background_agent.py > "logs/grok_analysis_${TIMESTAMP}.log" 2>&1 &

# Get the process ID
PID=$!

echo "✅ Background analysis started with PID: $PID"
echo "📊 To monitor progress:"
echo "   tail -f logs/grok_analysis_${TIMESTAMP}.log"
echo ""
echo "🛑 To stop the analysis:"
echo "   kill $PID"
echo ""
echo "📁 Output files will be saved to:"
echo "   ../json_files/upsc_prelims_2025_grok_analyzed.json"
echo "   ../json_files/upsc_prelims_2024_grok_analyzed.json"
echo ""
echo "🎯 You can now continue with other tasks while analysis runs in background!" 