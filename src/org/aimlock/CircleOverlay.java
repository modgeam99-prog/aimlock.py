package org.aimlock;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;

public class CircleOverlay {
    private Context context;
    private WindowManager wm;
    private View view;
    private int fov = 150;
    private float targetX = -1, targetY = -1;

    public CircleOverlay(Context ctx) {
        this.context = ctx;
        this.wm = (WindowManager) ctx.getSystemService(Context.WINDOW_SERVICE);
    }

    public void show() {
        view = new View(context) {
            Paint circle = new Paint();
            Paint cross = new Paint();
            Paint dot = new Paint();
            {
                circle.setColor(Color.argb(220, 0, 255, 128));
                circle.setStyle(Paint.Style.STROKE);
                circle.setStrokeWidth(6);
                circle.setAntiAlias(true);
                cross.setColor(Color.argb(230, 255, 50, 50));
                cross.setStyle(Paint.Style.STROKE);
                cross.setStrokeWidth(4);
                cross.setAntiAlias(true);
                dot.setColor(Color.argb(255, 255, 255, 0));
                dot.setStyle(Paint.Style.FILL);
                dot.setAntiAlias(true);
            }
            @Override
            protected void onDraw(Canvas c) {
                super.onDraw(c);
                float cx = getWidth() / 2f;
                float cy = getHeight() / 2f;
                c.drawCircle(cx, cy, fov, circle);
                c.drawCircle(cx, cy, fov + 10, circle);
                c.drawLine(cx - 30, cy, cx + 30, cy, cross);
                c.drawLine(cx, cy - 30, cx, cy + 30, cross);
                c.drawCircle(cx, cy, 8, cross);
                if (targetX >= 0 && targetY >= 0) {
                    c.drawCircle(targetX, targetY, 18, dot);
                }
            }
        };
        int type = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        int flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                  | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                  | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                  | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS;
        WindowManager.LayoutParams params = new WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.MATCH_PARENT,
            type, flags, PixelFormat.TRANSLUCENT
        );
        params.gravity = Gravity.TOP | Gravity.START;
        wm.addView(view, params);
    }

    public void setFov(int f) { this.fov = f; if (view != null) view.invalidate(); }
    public void setTarget(float x, float y) {
        this.targetX = x; this.targetY = y;
        if (view != null) view.invalidate();
    }
    public void hide() { if (view != null) { wm.removeView(view); view = null; } }
  }
