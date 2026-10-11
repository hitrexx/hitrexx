package ru.yudom.project;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.Optional;

@Service
public class ProjectService {

    private final List<Project> projects;

    public ProjectService(ObjectMapper mapper) throws IOException {
        try (InputStream in = new ClassPathResource("projects.json").getInputStream()) {
            this.projects = List.copyOf(mapper.readValue(in, new TypeReference<List<Project>>() {}));
        }
    }

    public List<Project> findAll() {
        return projects;
    }

    public Optional<Project> findById(String id) {
        return projects.stream().filter(p -> p.id().equals(id)).findFirst();
    }
}
