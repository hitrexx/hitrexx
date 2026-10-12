package ru.yudom.project;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/projects")
public class ProjectController {

    private final ProjectService projects;

    public ProjectController(ProjectService projects) {
        this.projects = projects;
    }

    @GetMapping
    public List<Project> all() {
        return projects.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Project> one(@PathVariable String id) {
        return ResponseEntity.of(projects.findById(id));
    }
}
