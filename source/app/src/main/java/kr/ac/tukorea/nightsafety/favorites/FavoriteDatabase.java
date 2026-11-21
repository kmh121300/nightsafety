package kr.ac.tukorea.nightsafety.favorites;

import androidx.room.Database;
import androidx.room.RoomDatabase;

@Database(entities = {FavoriteRoute.class}, version = 1, exportSchema = false)
public abstract class FavoriteDatabase extends RoomDatabase {
    public abstract FavoriteDao favorites();
}
