"""
Flask Application - Test Case Generator
Handles HTTP routes and coordinates between services
"""

import logging
from flask import Flask, request, jsonify, send_file, render_template
from services.gemini_service import GeminiService
from services.csv_service import CSVService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize services
logger.info("Initializing services...")
gemini_service = GeminiService(model_name="gemini-2.5-pro", temperature=0)
csv_service = CSVService(output_directory="generated_test_cases")
logger.info("Services initialized successfully")


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """
    Handle test case generation request.

    Expects JSON body:
        {
            "user_story": str,
            "filename": str (optional)
        }

    Returns:
        JSON response with success status and result
    """
    print("\n" + "="*70)
    print("NEW REQUEST RECEIVED")
    print("="*70)

    try:
        logger.info("="*70)
        logger.info("New generation request received")

        # Get request data
        data = request.json
        print(f"Request data received: {data is not None}")

        user_story = data.get('user_story', '').strip()
        filename = data.get('filename', 'test_cases').strip()

        print(f"Filename requested: {filename}")
        print(f"User story length: {len(user_story)} characters")

        logger.info(f"Filename requested: {filename}")
        logger.info(f"User story length: {len(user_story)} characters")

        # Validate input
        if not user_story:
            print("ERROR: Empty user story")
            logger.warning("Empty user story provided")
            return jsonify({
                "success": False,
                "message": "Please provide a user story"
            }), 400

        # Generate test cases using Gemini
        print("\nStep 1: Generating test cases with Gemini...")
        logger.info("Step 1: Generating test cases with Gemini...")
        gemini_result = gemini_service.generate_test_cases(user_story)

        print(f"Gemini result: {gemini_result}")

        if not gemini_result["success"]:
            print(f"ERROR: Gemini generation failed: {gemini_result['error']}")
            logger.error(f"Gemini generation failed: {gemini_result['error']}")
            return jsonify({
                "success": False,
                "message": f"Failed to generate test cases: {gemini_result['error']}"
            }), 500

        test_cases = gemini_result["test_cases"]
        print(f"Step 1 Complete: Generated {len(test_cases)} test cases")
        logger.info(f"Step 1 Complete: Generated {len(test_cases)} test cases")

        # Save to CSV
        print("\nStep 2: Saving test cases to CSV...")
        logger.info("Step 2: Saving test cases to CSV...")
        csv_result = csv_service.save_test_cases(test_cases, filename)

        print(f"CSV result: {csv_result}")

        if not csv_result["success"]:
            print(f"ERROR: CSV save failed: {csv_result['error']}")
            logger.error(f"CSV save failed: {csv_result['error']}")
            return jsonify({
                "success": False,
                "message": f"Failed to save CSV: {csv_result['error']}"
            }), 500

        print(f"Step 2 Complete: Saved to {csv_result['filename']}")
        print(f"Full path: {csv_result['filepath']}")
        logger.info(f"Step 2 Complete: Saved to {csv_result['filename']}")
        logger.info("✅ REQUEST COMPLETED SUCCESSFULLY")
        logger.info("="*70)

        # Prepare response
        response_data = {
            "success": True,
            "message": f"Successfully generated {csv_result['count']} test cases",
            "filename": csv_result["filename"],
            "filepath": csv_result["filepath"],
            "count": csv_result["count"]
        }

        print("\nResponse being sent:")
        print(response_data)
        print("="*70 + "\n")

        # Return success response
        return jsonify(response_data), 200

    except Exception as e:
        print(f"\n❌ EXCEPTION OCCURRED: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Unexpected error in /generate: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }), 500


@app.route('/download/<filename>')
def download(filename):
    """
    Download a generated CSV file.

    Args:
        filename (str): Name of the file to download

    Returns:
        File download response or 404 if not found
    """
    try:
        if csv_service.file_exists(filename):
            filepath = csv_service.get_file_path(filename)
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({
                "success": False,
                "message": "File not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error downloading file: {str(e)}"
        }), 500


@app.route('/files', methods=['GET'])
def list_files():
    """
    List all generated CSV files.

    Returns:
        JSON response with list of files
    """
    try:
        files = csv_service.list_files()
        return jsonify({
            "success": True,
            "files": files,
            "count": len(files)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error listing files: {str(e)}"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON response with service status
    """
    return jsonify({
        "status": "healthy",
        "gemini_service": gemini_service.get_model_info(),
        "csv_service": {
            "output_directory": csv_service.get_output_directory(),
            "files_count": len(csv_service.list_files())
        }
    })


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Starting Test Case Generator...")
    print("="*70)
    print("📍 URL: http://127.0.0.1:8000")
    print("📁 Output Directory:", csv_service.get_output_directory())
    print("🤖 AI Model:", gemini_service.model_name)
    print("="*70)
    print("\n⚡ Server is running - Press Ctrl+C to stop\n")
    print("Waiting for requests...\n")

    app.run(debug=True, port=8000, host='127.0.0.1')