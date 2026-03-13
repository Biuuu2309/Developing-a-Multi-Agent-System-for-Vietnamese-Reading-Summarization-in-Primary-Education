package com.example.my_be.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.Tag;

@Repository
public interface TagRepository extends JpaRepository<Tag, String> {

    Optional<Tag> findByName(String name); // Find a tag by its unique name
    List<Tag> findAllByName(String name); // Find all tags by name
}
