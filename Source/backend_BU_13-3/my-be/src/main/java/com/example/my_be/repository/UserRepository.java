package com.example.my_be.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.User;

@Repository
public interface UserRepository extends JpaRepository<User, String> {
    Optional<User> findByUsername(String username);
    Optional<User> findTop1ByUsername(String username);

    List<User> findByRole(String role);

    List<User> findByRoleNot(String role);
    Optional<User> findByEmail(String email);

    List<User> findByRoleAndUsernameNot(String role, String username);
    //getId
    
}
