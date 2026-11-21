package kr.ac.tukorea.nightsafety.favorites;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

/** Explicitly saved endpoints and an optional snapshot produced by our OSM routing server. */
@Entity(tableName = "favorites")
public class FavoriteRoute {
    @PrimaryKey(autoGenerate = true)
    public long id;
    @NonNull public String title = "";
    public double originLatitude;
    public double originLongitude;
    public double destinationLatitude;
    public double destinationLongitude;
    @NonNull public String originLabel = "";
    @NonNull public String destinationLabel = "";
    @NonNull public String originSource = "user_coordinate";
    @NonNull public String destinationSource = "user_coordinate";
    @NonNull public String preferredProfile = "balanced";
    public String snapshotJson;
    public long savedAt;
    public long createdAt;
    public long modifiedAt;
}
