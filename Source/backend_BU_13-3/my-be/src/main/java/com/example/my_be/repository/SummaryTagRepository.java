package com.example.my_be.repository;

import com.example.my_be.model.SummaryTag;
import com.example.my_be.model.Summary;
import com.example.my_be.model.Tag;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SummaryTagRepository extends JpaRepository<SummaryTag, String> {

    List<SummaryTag> findBySummary(Summary summary); // Find all tags for a specific summary

    List<SummaryTag> findByTag(Tag tag); // Find all summaries associated with a specific tag
}
