import asyncio
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from curry_detector import CurryDetector
import base64
import json

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = CurryDetector()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive image data from client
            data = await websocket.receive_text()
            json_data = json.loads(data)
            
            if json_data.get('type') == 'image':
                # Decode base64 image
                image_bytes = base64.b64decode(json_data['image'].split(',')[1])
                nparr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Process image
                result = detector.calculate_thickness(frame)
                
                # Convert processed images to base64
                result['frame'] = base64.b64encode(result['frame']).decode('utf-8')
                result['mask'] = base64.b64encode(result['mask']).decode('utf-8')
                result['reflection_mask'] = base64.b64encode(result['reflection_mask']).decode('utf-8')
                
                # Send results back
                await websocket.send_text(json.dumps({
                    'type': 'result',
                    'data': result
                }))
                
            await asyncio.sleep(0.1)  # Prevent overloading
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

# For serving static files in production
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")