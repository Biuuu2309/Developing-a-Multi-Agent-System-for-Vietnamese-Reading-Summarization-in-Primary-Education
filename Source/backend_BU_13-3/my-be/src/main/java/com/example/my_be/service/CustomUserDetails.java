package com.example.my_be.service;

import com.example.my_be.model.User;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.Collections;

public class CustomUserDetails implements UserDetails {

    private User user;

    public CustomUserDetails(User user) {
        this.user = user;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        // Chuyển đổi role từ database sang GrantedAuthority
        return Collections.singletonList(new SimpleGrantedAuthority("ROLE_" +
                user.getRole()));
    }

    @Override
    public String getPassword() {
        return user.getPassword();
    }

    @Override
    public String getUsername() {
        return user.getUsername();
    }

    @Override
    public boolean isAccountNonExpired() {
        return true; // Hoặc thêm logic để kiểm tra account hết hạn
    }

    @Override
    public boolean isAccountNonLocked() {
        return true; // Hoặc thêm logic để kiểm tra account bị khóa
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true; // Hoặc thêm logic để kiểm tra credentials hết hạn
    }

    @Override
    public boolean isEnabled() {
        return true; // Hoặc thêm logic để kiểm tra account có được kích hoạt hay

    }
}
