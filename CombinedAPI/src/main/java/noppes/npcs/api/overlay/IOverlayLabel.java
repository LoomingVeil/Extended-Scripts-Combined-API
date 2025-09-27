package noppes.npcs.api.overlay;

public interface IOverlayLabel extends ICustomOverlayComponent {
    String getText();

    IOverlayLabel setText(String var1);

    int getWidth();

    int getHeight();

    IOverlayLabel setSize(int var1, int var2);

    float getScale();

    IOverlayLabel setScale(float var1);

    boolean getShadow();

    void setShadow(boolean shadow);

    /**
     * Gets the width of the string in pixels. This can be useful for centering text.
     * Having certain non-standard special characters may produce inaccurate results.
     */
    int getStringWidth();

}