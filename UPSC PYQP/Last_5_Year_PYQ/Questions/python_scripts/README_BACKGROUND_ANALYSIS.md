# Background Grok Analysis System

This system provides automated background processing of UPSC questions using Grok AI with optimized batch processing for cost efficiency and reliability.

## 🚀 Quick Start

### 1. Start Background Analysis
```bash
./run_background_analysis.sh
```

### 2. Monitor Progress
```bash
python3 monitor_analysis.py
```

### 3. View Live Logs
```bash
tail -f logs/grok_analysis_*.log
```

## 📁 Files Overview

### Core Scripts
- `grok_analysis_background_agent.py` - Main background processing agent
- `run_background_analysis.sh` - Shell script to start background analysis
- `monitor_analysis.py` - Progress monitoring script

### Test Scripts
- `grok_analysis_upsc_2025_batch.py` - Test script for batch processing
- `grok_analysis_upsc_2025.py` - Original individual processing script

### Documentation
- `grok_4_documentation.md` - Grok API reference and pricing
- `README_BACKGROUND_ANALYSIS.md` - This file

## 🎯 Features

### ✅ Cost Optimization
- **80% cost reduction**: 40 API calls instead of 200
- **Batch processing**: 5 questions per API call
- **Estimated savings**: $2,880 for both years

### ✅ Reliability
- **Enhanced JSON parsing**: Multiple fallback methods
- **Progressive saving**: Saves after each batch
- **Retry logic**: 3 attempts with fallback analysis
- **Comprehensive logging**: Detailed progress tracking

### ✅ Background Processing
- **Non-blocking**: Runs in background while you work
- **Process management**: Easy start/stop/monitor
- **Progress tracking**: Real-time status updates
- **Error recovery**: Continues even if some batches fail

## 📊 Processing Details

### UPSC 2025
- **Questions**: 100
- **Batches**: 20 (5 questions each)
- **Estimated time**: 30-45 minutes
- **Estimated cost**: ~$360

### UPSC 2024
- **Questions**: 100
- **Batches**: 20 (5 questions each)
- **Estimated time**: 30-45 minutes
- **Estimated cost**: ~$360

### Total
- **Questions**: 200
- **API calls**: 40 (vs 200 individual)
- **Total time**: 60-90 minutes
- **Total cost**: ~$720 (vs ~$3,600)

## 🔧 Usage Commands

### Start Analysis
```bash
# Start background analysis
./run_background_analysis.sh

# Or run directly
python3 grok_analysis_background_agent.py
```

### Monitor Progress
```bash
# Check current status
python3 monitor_analysis.py

# View live logs
tail -f logs/grok_analysis_*.log

# View specific log file
cat logs/grok_analysis_YYYYMMDD_HHMMSS.log
```

### Stop Analysis
```bash
# Find process ID
ps aux | grep grok_analysis_background_agent.py

# Stop the process
kill <PID>
```

## 📁 Output Files

### Progress Files (During Processing)
- `../json_files/upsc_prelims_2025_grok_progress_batch_*.json`
- `../json_files/upsc_prelims_2024_grok_progress_batch_*.json`

### Final Output Files
- `../json_files/upsc_prelims_2025_grok_analyzed_complete.json`
- `../json_files/upsc_prelims_2024_grok_analyzed_complete.json`

### Log Files
- `logs/grok_analysis_YYYYMMDD_HHMMSS.log`

## 🔍 Analysis Fields

Each question gets 18 comprehensive analysis fields:

1. **explanation** - Mentor-like explanation of correct answer
2. **primary_type** - Main subject area
3. **secondary_type** - Specific sub-topic
4. **difficulty_level** - Easy/Medium/Hard
5. **difficulty_reason** - Why this difficulty level
6. **learning_objectives** - What knowledge is needed
7. **question_strategy** - How question is designed
8. **options_analysis** - Detailed analysis of each option
9. **key_concepts** - Key concepts tested
10. **common_mistakes** - Common mistakes aspirants make
11. **elimination_technique** - How to eliminate wrong options
12. **memory_hooks** - Memory techniques
13. **related_topics** - Related topics for preparation
14. **exam_strategy** - Time management and confidence
15. **source_material** - Recommended sources
16. **motivation** - Why this is important
17. **examiner_thought_process** - What examiner is thinking
18. **current_affairs_connection** - Current events connection
19. **time_management** - Recommended time allocation
20. **confidence_calibration** - How to assess confidence

## ⚙️ Configuration

### Environment Variables
```bash
# Required in .env file
GROK_API_KEY=your_grok_api_key_here
```

### Batch Size
- **Default**: 5 questions per batch
- **Configurable**: Change `batch_size` parameter in `analyze_year_questions()`

### Timeouts
- **API timeout**: 180 seconds per batch
- **Retry delays**: 5-20 seconds between attempts
- **Rate limiting**: 15 seconds between batches

## 🛠️ Troubleshooting

### Common Issues

#### API Key Issues
```bash
# Check if API key is set
echo $GROK_API_KEY

# Verify in .env file
cat ../../../../.env | grep GROK_API_KEY
```

#### File Path Issues
```bash
# Ensure you're in the right directory
pwd
# Should be: .../python_scripts

# Check if input files exist
ls -la ../json_files/upsc_prelims_2025_structured_for_frontend.json
ls -la ../json_files/upsc_prelims_2024_structured_for_frontend.json
```

#### Process Issues
```bash
# Check if background process is running
ps aux | grep grok_analysis_background_agent.py

# Check log files for errors
tail -n 50 logs/grok_analysis_*.log
```

### Error Recovery

#### If Analysis Fails Mid-Process
1. Check log files for specific errors
2. Restart the analysis - it will continue from where it left off
3. Progress files are saved after each batch

#### If JSON Parsing Fails
- The system has multiple fallback methods
- Fallback analysis is provided for failed questions
- Check logs for specific parsing errors

#### If API Rate Limits Hit
- The system includes 15-second delays between batches
- If still hitting limits, increase delay in the script

## 📈 Performance Monitoring

### Real-time Monitoring
```bash
# Monitor live progress
tail -f logs/grok_analysis_*.log

# Check progress every 5 minutes
watch -n 300 python3 monitor_analysis.py
```

### Cost Tracking
- Monitor API usage in Grok dashboard
- Expected: ~40 API calls total
- Expected cost: ~$720 for both years

### Time Tracking
- UPSC 2025: ~30-45 minutes
- UPSC 2024: ~30-45 minutes
- Total: ~60-90 minutes

## 🎉 Success Indicators

### Analysis Complete When:
1. Both complete files exist:
   - `upsc_prelims_2025_grok_analyzed_complete.json`
   - `upsc_prelims_2024_grok_analyzed_complete.json`

2. Log shows completion message:
   ```
   🎉 Background Analysis Complete!
   📊 Total questions processed: 200
   ```

3. Monitor shows 100% completion for both years

## 🔄 Next Steps

After analysis completes:
1. Verify output files contain all 200 questions
2. Check analysis quality on sample questions
3. Integrate with frontend application
4. Consider processing additional years (2021-2023)

## 📞 Support

For issues or questions:
1. Check log files first
2. Review this README
3. Check Grok API documentation
4. Verify environment setup

---

**Happy Analyzing! 🚀** 