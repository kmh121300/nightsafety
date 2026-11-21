package kr.ac.tukorea.nightsafety.favorites;

import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.Query;
import androidx.room.Update;
import java.util.List;

@Dao
public interface FavoriteDao {
    @Query("SELECT * FROM favorites ORDER BY modifiedAt DESC, id DESC")
    List<FavoriteRoute> list();

    @Query("SELECT * FROM favorites WHERE id = :id")
    FavoriteRoute get(long id);

    @Insert
    long insert(FavoriteRoute route);

    @Update
    int update(FavoriteRoute route);

    @Query("UPDATE favorites SET title = :title, preferredProfile = :profile, modifiedAt = :modifiedAt WHERE id = :id")
    int rename(long id, String title, String profile, long modifiedAt);

    @Query("DELETE FROM favorites WHERE id = :id")
    int delete(long id);
}
