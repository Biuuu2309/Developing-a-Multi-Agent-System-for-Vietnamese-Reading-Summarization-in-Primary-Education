package com.example.my_be.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.Summary;
import com.example.my_be.model.User;

@Repository
public interface SummaryRepository extends JpaRepository<Summary, String> {

    List<Summary> findByCreatedBy(User createdBy);

    List<Summary> findByStatus(String status);

    List<Summary> findByGrade(String grade);
    List<Summary> findTop10ByOrderByReadCountDesc(); // Fetch top 10 summaries ordered by readCount
    List<Summary> findByTitleContainingOrContentContainingOrStatusContainingOrMethodContainingOrGradeContaining(
        String title, String content, String status, String method, String grade
    );

    List<Summary> findByTitleContainingIgnoreCase(@Param("title") String title);

    @Query("SELECT s FROM Summary s WHERE (LOWER(s.title) LIKE LOWER(CONCAT('%', :searchTerm, '%'))) AND (LOWER(s.grade) = LOWER(:grade) OR :grade = '')")
    List<Summary> findByTitleContainingIgnoreCaseAndGrade(
        @Param("searchTerm") String searchTerm, @Param("grade") String grade);



    List<Summary> findByMethod(String method); // Filter summaries by method (PHOBERT or T5_DIEN_GIAI)

    @Query("SELECT s FROM Summary s LEFT JOIN FETCH s.createdBy WHERE s.summaryId = :id")
Optional<Summary> getSummaryByIdwoStatus(@Param("id") String id);
}
