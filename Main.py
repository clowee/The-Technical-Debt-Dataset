from Projects import Projects

COURSE_SERVER = "https://course-sonar.rd.tuni.fi/"
SONAR63 = "http://sonar63.rd.tut.fi/"
ORGANIZATION = "default-organization"


def main():
    prj = Projects(SONAR63, ORGANIZATION)
    projects = prj.get_projects()


if __name__ == '__main__':
    main()
