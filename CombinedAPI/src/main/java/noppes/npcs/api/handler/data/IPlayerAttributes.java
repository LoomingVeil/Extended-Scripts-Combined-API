package noppes.npcs.api.handler.data;

import noppes.npcs.api.entity.IPlayer;
import org.spongepowered.asm.mixin.Unique;
import noppes.npcs.api.item.IItemStack;

/**
 * Represents a collection of a player's custom attributes.
 * <p>
 * Expose methods to retrieve all attribute instances as an array, look up individual attributes by key,
 * and check for the presence of a specific attribute.
 * </p>
 */
public interface IPlayerAttributes {

    /**
     * Recalulates Item Attributes on a Player
     */
    void recalculate(IPlayer player);

    /**
     * Returns an array of all custom attribute instances associated with the player.
     *
     * @return an array of {@link ICustomAttribute} objects
     */
    ICustomAttribute[] getAttributes();

    /**
     * Returns the value of the attribute identified by the given key.
     *
     * @param key the attribute key (e.g., "health", "movement_speed")
     * @return the float value of the attribute, or 0 if the attribute is not found
     */
    float getAttributeValue(String key);

    /**
     * Checks whether an attribute with the given key exists.
     *
     * @param key the attribute key to check
     * @return true if the attribute exists, false otherwise
     */
    boolean hasAttribute(String key);

    /**
     * Returns the custom attribute instance identified by the given key.
     *
     * @param key the attribute key (e.g., "health", "movement_speed")
     * @return the corresponding {@link ICustomAttribute} instance, or null if not found
     */
    ICustomAttribute getAttribute(String key);

    String getAttributeKeys();

    String getCoreAttributeKeys();

    boolean hasCoreAttribute(String key);

    /**
     * Gets the attribute core as an item that can be given to the player.
     * @param canBeRedeemed When true and right-clicking the core for 3 seconds will give you all the attributes associated with the core.
     */
    IItemStack getAttributeCore(boolean canBeRedeemed);

    /**
     * Gets the attribute core as an item that can be given to the player.
     */
    IItemStack getAttributeCore();

    void resetCoreAttributes();

    /**
     * Gets core attributes. These attributes are separate from equipment attributes.
     */
    float getCoreAttribute(String key);

    void modifyCoreAttribute(String key, float delta);

    /**
     * Gives attributes to the player. These attributes are the same that can be applied to item except these attributes are always active until removed.
     */
    void setCoreAttribute(String key, float value);

}