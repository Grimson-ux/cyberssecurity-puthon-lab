import Header from "./components/Header";
import MainInfoSection from "./components/MainInfoSection";
import SkillsSection from "./components/SkillsSection";
import EducationSection from "./components/EducationSection";
import Footer from "./components/Footer";

function App() {
  return (
    <>
      <Header />

      <main>
        <MainInfoSection />
        <SkillsSection />
        <EducationSection />
      </main>

      <Footer />
    </>
  );
}

export default App;