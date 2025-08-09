{
  "version"; 2,
  "builds"; [
    {
      "src": "backend/main.py",
      "use": "@vercel/python",
      "config": { 
        "maxLambdaSize": "15mb",
        "runtime": "python3.9"
      }
    },
    {
      "src": "frontend/**",
      "use": "@vercel/static"
    }
  ],
  "routes"; [
    {
      "src": "/ws",
      "dest": "backend/main.py",
      "continue": true
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ]
}